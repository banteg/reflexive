#define _CRT_SECURE_NO_WARNINGS

#include <windows.h>

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BREAKPOINT 0xCC

typedef struct {
    char packed_path[MAX_PATH];
    char output_path[MAX_PATH];
    DWORD target_address;
    DWORD image_base;
    DWORD image_size;
    DWORD size_of_headers;
    DWORD entry_rva;
} DumpState;

static void fail(const char *message) {
    fprintf(stderr, "error: %s\n", message);
}

static int read_remote(HANDLE process, LPCVOID address, void *buffer, SIZE_T size) {
    SIZE_T read_count = 0;
    return ReadProcessMemory(process, address, buffer, size, &read_count) && read_count == size;
}

static int write_remote(HANDLE process, LPVOID address, const void *buffer, SIZE_T size) {
    SIZE_T written = 0;
    return WriteProcessMemory(process, address, buffer, size, &written) && written == size;
}

static int arm_breakpoint(HANDLE process, DWORD address, BYTE *original_byte) {
    if (!read_remote(process, (LPCVOID)(uintptr_t)address, original_byte, 1)) {
        return 0;
    }
    return write_remote(process, (LPVOID)(uintptr_t)address, &(BYTE){BREAKPOINT}, 1);
}

static int restore_breakpoint(HANDLE process, DWORD address, BYTE original_byte) {
    return write_remote(process, (LPVOID)(uintptr_t)address, &original_byte, 1);
}

static int write_file_bytes(const char *path, const BYTE *buffer, DWORD size) {
    HANDLE handle = CreateFileA(path, GENERIC_WRITE, 0, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD written = 0;

    if (handle == INVALID_HANDLE_VALUE) {
        return 0;
    }

    if (!WriteFile(handle, buffer, size, &written, NULL) || written != size) {
        CloseHandle(handle);
        return 0;
    }

    CloseHandle(handle);
    return 1;
}

static int capture_headers(HANDLE process, DumpState *state) {
    BYTE headers[0x1000];
    IMAGE_DOS_HEADER *dos;
    IMAGE_NT_HEADERS32 *nt;

    if (!read_remote(process, (LPCVOID)(uintptr_t)state->image_base, headers, sizeof(headers))) {
        fail("unable to read remote headers");
        return 0;
    }

    dos = (IMAGE_DOS_HEADER *)headers;
    if (dos->e_magic != IMAGE_DOS_SIGNATURE) {
        fail("remote image is not a PE");
        return 0;
    }

    if ((DWORD)dos->e_lfanew + sizeof(IMAGE_NT_HEADERS32) > sizeof(headers)) {
        fail("remote PE headers exceed local header buffer");
        return 0;
    }

    nt = (IMAGE_NT_HEADERS32 *)(headers + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) {
        fail("remote NT headers are invalid");
        return 0;
    }

    state->image_size = nt->OptionalHeader.SizeOfImage;
    state->size_of_headers = nt->OptionalHeader.SizeOfHeaders;
    state->entry_rva = nt->OptionalHeader.AddressOfEntryPoint;
    return 1;
}

static int dump_remote_image(HANDLE process, DumpState *state) {
    BYTE *buffer = (BYTE *)malloc(state->image_size);
    int ok = 0;

    if (buffer == NULL) {
        fail("unable to allocate dump buffer");
        return 0;
    }

    if (!read_remote(process, (LPCVOID)(uintptr_t)state->image_base, buffer, state->image_size)) {
        fail("unable to read unpacked image");
        goto cleanup;
    }

    if (!write_file_bytes(state->output_path, buffer, state->image_size)) {
        fail("unable to write dump file");
        goto cleanup;
    }

    ok = 1;

cleanup:
    free(buffer);
    return ok;
}

static int capture_image(DumpState *state) {
    STARTUPINFOA startup_info;
    PROCESS_INFORMATION process_info;
    DEBUG_EVENT event;
    BYTE original_byte = 0;
    int first_breakpoint = 1;
    int target_armed = 0;
    int captured = 0;
    DWORD started_at = GetTickCount();

    ZeroMemory(&startup_info, sizeof(startup_info));
    ZeroMemory(&process_info, sizeof(process_info));
    startup_info.cb = sizeof(startup_info);

    if (!CreateProcessA(
            state->packed_path,
            NULL,
            NULL,
            NULL,
            FALSE,
            DEBUG_PROCESS | DEBUG_ONLY_THIS_PROCESS,
            NULL,
            NULL,
            &startup_info,
            &process_info)) {
        fail("unable to launch debuggee");
        return 0;
    }

    while (GetTickCount() - started_at < 30000) {
        if (!WaitForDebugEvent(&event, 250)) {
            continue;
        }

        if (event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT) {
            state->image_base = (DWORD)(uintptr_t)event.u.CreateProcessInfo.lpBaseOfImage;
            if (event.u.CreateProcessInfo.hFile != NULL) {
                CloseHandle(event.u.CreateProcessInfo.hFile);
            }
        } else if (event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT &&
                   event.u.Exception.ExceptionRecord.ExceptionCode == EXCEPTION_BREAKPOINT) {
            DWORD exception_address = (DWORD)(uintptr_t)event.u.Exception.ExceptionRecord.ExceptionAddress;

            if (first_breakpoint) {
                first_breakpoint = 0;
                if (!target_armed) {
                    if (!arm_breakpoint(process_info.hProcess, state->target_address, &original_byte)) {
                        fail("unable to set target breakpoint");
                        break;
                    }
                    target_armed = 1;
                }
            } else if (exception_address == state->target_address) {
                HANDLE thread_handle = OpenThread(THREAD_GET_CONTEXT | THREAD_SET_CONTEXT, FALSE, event.dwThreadId);
                CONTEXT context;

                if (thread_handle == NULL) {
                    fail("unable to open debuggee thread");
                    break;
                }

                ZeroMemory(&context, sizeof(context));
                context.ContextFlags = CONTEXT_FULL;
                if (!GetThreadContext(thread_handle, &context)) {
                    CloseHandle(thread_handle);
                    fail("unable to read thread context");
                    break;
                }

                context.Eip -= 1;
                if (!SetThreadContext(thread_handle, &context)) {
                    CloseHandle(thread_handle);
                    fail("unable to rewind thread context");
                    break;
                }

                if (!restore_breakpoint(process_info.hProcess, state->target_address, original_byte)) {
                    CloseHandle(thread_handle);
                    fail("unable to restore target opcode");
                    break;
                }

                if (!capture_headers(process_info.hProcess, state) || !dump_remote_image(process_info.hProcess, state)) {
                    CloseHandle(thread_handle);
                    break;
                }

                captured = 1;
                CloseHandle(thread_handle);
                break;
            }
        }

        if (!ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE)) {
            fail("unable to continue debuggee");
            break;
        }
    }

    TerminateProcess(process_info.hProcess, 0);
    CloseHandle(process_info.hThread);
    CloseHandle(process_info.hProcess);

    if (!captured) {
        fail("timed out before reaching unpacked entrypoint");
    }
    return captured;
}

int main(int argc, char **argv) {
    DumpState state;
    char *end = NULL;

    if (argc != 4) {
        fprintf(stderr, "usage: mpress_memory_dumper.exe <packed.exe> <target_va_hex> <output_image.bin>\n");
        return 1;
    }

    ZeroMemory(&state, sizeof(state));
    strncpy(state.packed_path, argv[1], sizeof(state.packed_path) - 1);
    strncpy(state.output_path, argv[3], sizeof(state.output_path) - 1);
    state.target_address = (DWORD)strtoul(argv[2], &end, 16);
    if (end == NULL || *end != '\0' || state.target_address == 0) {
        fail("invalid target virtual address");
        return 1;
    }

    return capture_image(&state) ? 0 : 1;
}

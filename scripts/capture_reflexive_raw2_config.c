#define _CRT_SECURE_NO_WARNINGS

#include <windows.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BREAKPOINT 0xCC
#define MAX_TEXT 32768

typedef struct {
    char wrapper_path[MAX_PATH];
    char wrapper_dir[MAX_PATH];
    DWORD target_rva;
    DWORD target_address;
    DWORD return_address;
    DWORD config_path_ptr;
    DWORD config_output_slot;
    DWORD seed1;
    DWORD seed2_slot;
    DWORD seed2;
    DWORD decrypted_config_ptr;
    char config_path[MAX_PATH];
    char decrypted_config[MAX_TEXT];
} CaptureState;

static void fail(const char *message) {
    fprintf(stderr, "error: %s\n", message);
}

static void dirname_from_path(const char *path, char *buffer, size_t size) {
    size_t len;

    strncpy(buffer, path, size - 1);
    buffer[size - 1] = '\0';
    len = strlen(buffer);

    while (len > 0) {
        char c = buffer[len - 1];
        if (c == '\\' || c == '/') {
            buffer[len - 1] = '\0';
            return;
        }
        len -= 1;
    }

    buffer[0] = '.';
    buffer[1] = '\0';
}

static int read_remote(HANDLE process, LPCVOID address, void *buffer, SIZE_T size) {
    SIZE_T read_count = 0;
    return ReadProcessMemory(process, address, buffer, size, &read_count) && read_count == size;
}

static int write_remote(HANDLE process, LPVOID address, const void *buffer, SIZE_T size) {
    SIZE_T written = 0;
    return WriteProcessMemory(process, address, buffer, size, &written) && written == size;
}

static int read_remote_dword(HANDLE process, DWORD address, DWORD *value) {
    return read_remote(process, (LPCVOID)(uintptr_t)address, value, sizeof(*value));
}

static int read_remote_string(HANDLE process, DWORD remote_ptr, char *buffer, size_t size) {
    size_t offset = 0;

    if (size == 0) {
        return 0;
    }
    buffer[0] = '\0';

    if (remote_ptr == 0) {
        return 1;
    }

    while (offset + 1 < size) {
        char c;
        if (!read_remote(process, (LPCVOID)(uintptr_t)(remote_ptr + (DWORD)offset), &c, 1)) {
            return 0;
        }
        buffer[offset++] = c;
        if (c == '\0') {
            return 1;
        }
    }

    buffer[size - 1] = '\0';
    return 1;
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

static int capture_raw2(CaptureState *state) {
    STARTUPINFOA startup_info;
    PROCESS_INFORMATION process_info;
    DEBUG_EVENT event;
    DWORD base_address = 0;
    DWORD active_breakpoint = 0;
    BYTE original_byte = 0;
    int first_breakpoint = 1;
    int target_armed = 0;
    int return_armed = 0;
    int captured = 0;
    BOOL continue_needed = FALSE;
    DWORD started_at = GetTickCount();

    ZeroMemory(&startup_info, sizeof(startup_info));
    ZeroMemory(&process_info, sizeof(process_info));
    startup_info.cb = sizeof(startup_info);

    if (!CreateProcessA(
            state->wrapper_path,
            NULL,
            NULL,
            NULL,
            FALSE,
            DEBUG_PROCESS | DEBUG_ONLY_THIS_PROCESS,
            NULL,
            state->wrapper_dir,
            &startup_info,
            &process_info)) {
        fail("unable to launch wrapper under debugger");
        return 0;
    }

    while (GetTickCount() - started_at < 30000) {
        if (!WaitForDebugEvent(&event, 250)) {
            continue;
        }
        continue_needed = TRUE;

        if (event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT) {
            base_address = (DWORD)(uintptr_t)event.u.CreateProcessInfo.lpBaseOfImage;
            state->target_address = base_address + state->target_rva;
            if (event.u.CreateProcessInfo.hFile != NULL) {
                CloseHandle(event.u.CreateProcessInfo.hFile);
            }
        } else if (event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT &&
                   event.u.Exception.ExceptionRecord.ExceptionCode == EXCEPTION_BREAKPOINT) {
            DWORD exception_address = (DWORD)(uintptr_t)event.u.Exception.ExceptionRecord.ExceptionAddress;

            if (first_breakpoint) {
                first_breakpoint = 0;
                if (base_address != 0 && !target_armed) {
                    active_breakpoint = state->target_address;
                    if (!arm_breakpoint(process_info.hProcess, active_breakpoint, &original_byte)) {
                        fail("unable to set target breakpoint");
                        break;
                    }
                    target_armed = 1;
                }
            } else if (exception_address == active_breakpoint) {
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

                if (!restore_breakpoint(process_info.hProcess, active_breakpoint, original_byte)) {
                    CloseHandle(thread_handle);
                    fail("unable to restore original opcode");
                    break;
                }

                if (!return_armed) {
                    DWORD stack_base = context.Esp;

                    if (!read_remote_dword(process_info.hProcess, stack_base + 0, &state->return_address) ||
                        !read_remote_dword(process_info.hProcess, stack_base + 4, &state->config_path_ptr) ||
                        !read_remote_dword(process_info.hProcess, stack_base + 8, &state->config_output_slot) ||
                        !read_remote_dword(process_info.hProcess, stack_base + 12, &state->seed1) ||
                        !read_remote_dword(process_info.hProcess, stack_base + 16, &state->seed2_slot)) {
                        CloseHandle(thread_handle);
                        fail("unable to read decryptor arguments");
                        break;
                    }

                    if (!read_remote_string(process_info.hProcess, state->config_path_ptr, state->config_path, sizeof(state->config_path))) {
                        CloseHandle(thread_handle);
                        fail("unable to read config path");
                        break;
                    }

                    active_breakpoint = state->return_address;
                    if (!arm_breakpoint(process_info.hProcess, active_breakpoint, &original_byte)) {
                        CloseHandle(thread_handle);
                        fail("unable to set return breakpoint");
                        break;
                    }
                    return_armed = 1;
                } else {
                    if (!read_remote_dword(process_info.hProcess, state->config_output_slot, &state->decrypted_config_ptr) ||
                        !read_remote_dword(process_info.hProcess, state->seed2_slot, &state->seed2)) {
                        CloseHandle(thread_handle);
                        fail("unable to read decryptor outputs");
                        break;
                    }

                    if (!read_remote_string(process_info.hProcess, state->decrypted_config_ptr, state->decrypted_config, sizeof(state->decrypted_config))) {
                        CloseHandle(thread_handle);
                        fail("unable to read decrypted config");
                        break;
                    }

                    captured = 1;
                    continue_needed = FALSE;
                    CloseHandle(thread_handle);
                    break;
                }

                if (!ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE)) {
                    CloseHandle(thread_handle);
                    fail("unable to continue debuggee");
                    break;
                }
                continue_needed = FALSE;
                CloseHandle(thread_handle);
            }
        } else if (event.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT) {
            break;
        }

        if (continue_needed) {
            ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE);
        }
    }

    TerminateProcess(process_info.hProcess, 0);
    CloseHandle(process_info.hThread);
    CloseHandle(process_info.hProcess);

    if (!captured) {
        fail("timed out before capturing decrypted RAW_002");
        return 0;
    }
    return 1;
}

static void print_json_string(const char *value) {
    const unsigned char *p = (const unsigned char *)value;
    putchar('"');
    while (*p != '\0') {
        unsigned char c = *p++;
        switch (c) {
            case '\\':
                fputs("\\\\", stdout);
                break;
            case '"':
                fputs("\\\"", stdout);
                break;
            case '\n':
                fputs("\\n", stdout);
                break;
            case '\r':
                fputs("\\r", stdout);
                break;
            case '\t':
                fputs("\\t", stdout);
                break;
            default:
                if (c < 0x20) {
                    fprintf(stdout, "\\u%04x", c);
                } else {
                    putchar((int)c);
                }
                break;
        }
    }
    putchar('"');
}

int main(int argc, char **argv) {
    CaptureState state;
    char *end = NULL;

    if (argc != 3) {
        fprintf(stderr, "usage: %s <wrapper.exe> <decrypt_rva>\n", argv[0]);
        return 1;
    }

    ZeroMemory(&state, sizeof(state));
    strncpy(state.wrapper_path, argv[1], sizeof(state.wrapper_path) - 1);
    state.wrapper_path[sizeof(state.wrapper_path) - 1] = '\0';
    dirname_from_path(state.wrapper_path, state.wrapper_dir, sizeof(state.wrapper_dir));
    state.target_rva = (DWORD)strtoul(argv[2], &end, 0);
    if (end == argv[2] || *end != '\0') {
        fail("invalid decrypt_rva");
        return 1;
    }

    if (!capture_raw2(&state)) {
        return 1;
    }

    fputs("{\"wrapper_path\":", stdout);
    print_json_string(state.wrapper_path);
    fputs(",\"decrypt_rva\":", stdout);
    fprintf(stdout, "%lu", (unsigned long)state.target_rva);
    fputs(",\"seed1\":", stdout);
    fprintf(stdout, "%lu", (unsigned long)state.seed1);
    fputs(",\"seed2\":", stdout);
    fprintf(stdout, "%lu", (unsigned long)state.seed2);
    fputs(",\"config_path\":", stdout);
    print_json_string(state.config_path);
    fputs(",\"decrypted_config\":", stdout);
    print_json_string(state.decrypted_config);
    fputs("}\n", stdout);
    return 0;
}

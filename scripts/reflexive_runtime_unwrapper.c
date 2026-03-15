#define _CRT_SECURE_NO_WARNINGS

#include <windows.h>
#include <imagehlp.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_TEXT 4096
#define BREAKPOINT 0xCC

typedef struct {
    DWORD create_process_slot;
    DWORD open_process_slot;
    DWORD write_process_memory_slot;
} ImportSlots;

typedef struct {
    char wrapper_path[MAX_PATH];
    char wrapper_dir[MAX_PATH];
    char output_path[MAX_PATH];
    char child_path[MAX_PATH];
    DWORD child_process_id;
    DWORD remote_base_address;
    BYTE *decrypted;
    DWORD decrypted_size;
} CaptureState;

static void fail(const char *message) {
    fprintf(stderr, "error: %s\n", message);
}

static int read_file_bytes(const char *path, BYTE **buffer, DWORD *size_out) {
    HANDLE handle = CreateFileA(path, GENERIC_READ, FILE_SHARE_READ, NULL, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, NULL);
    DWORD size;
    BYTE *local_buffer;
    DWORD read_count = 0;

    if (handle == INVALID_HANDLE_VALUE) {
        return 0;
    }

    size = GetFileSize(handle, NULL);
    if (size == INVALID_FILE_SIZE || size == 0) {
        CloseHandle(handle);
        return 0;
    }

    local_buffer = (BYTE *)malloc(size);
    if (local_buffer == NULL) {
        CloseHandle(handle);
        return 0;
    }

    if (!ReadFile(handle, local_buffer, size, &read_count, NULL) || read_count != size) {
        free(local_buffer);
        CloseHandle(handle);
        return 0;
    }

    CloseHandle(handle);
    *buffer = local_buffer;
    *size_out = size;
    return 1;
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

static PIMAGE_NT_HEADERS pe_nt_headers(BYTE *buffer) {
    PIMAGE_DOS_HEADER dos = (PIMAGE_DOS_HEADER)buffer;
    PIMAGE_NT_HEADERS nt;

    if (dos->e_magic != IMAGE_DOS_SIGNATURE) {
        return NULL;
    }

    nt = (PIMAGE_NT_HEADERS)(buffer + dos->e_lfanew);
    if (nt->Signature != IMAGE_NT_SIGNATURE) {
        return NULL;
    }

    return nt;
}

static LPVOID image_rva_to_va(PIMAGE_NT_HEADERS nt, BYTE *buffer, DWORD rva) {
    return ImageRvaToVa(nt, buffer, rva, NULL);
}

static int find_kernel32_import_slots(BYTE *buffer, ImportSlots *slots) {
    PIMAGE_NT_HEADERS nt = pe_nt_headers(buffer);
    DWORD import_rva;
    PIMAGE_IMPORT_DESCRIPTOR descriptor;

    memset(slots, 0, sizeof(*slots));
    if (nt == NULL) {
        return 0;
    }

    import_rva = nt->OptionalHeader.DataDirectory[IMAGE_DIRECTORY_ENTRY_IMPORT].VirtualAddress;
    if (import_rva == 0) {
        return 0;
    }

    descriptor = (PIMAGE_IMPORT_DESCRIPTOR)image_rva_to_va(nt, buffer, import_rva);
    if (descriptor == NULL) {
        return 0;
    }

    while (descriptor->FirstThunk != 0) {
        const char *dll_name = (const char *)image_rva_to_va(nt, buffer, descriptor->Name);
        DWORD thunk_rva = descriptor->OriginalFirstThunk ? descriptor->OriginalFirstThunk : descriptor->FirstThunk;
        PIMAGE_THUNK_DATA thunk = (PIMAGE_THUNK_DATA)image_rva_to_va(nt, buffer, thunk_rva);
        DWORD first_thunk = descriptor->FirstThunk;

        if (dll_name != NULL && _stricmp(dll_name, "kernel32.dll") == 0 && thunk != NULL) {
            while (thunk->u1.AddressOfData != 0) {
                if ((thunk->u1.Ordinal & IMAGE_ORDINAL_FLAG32) == 0) {
                    PIMAGE_IMPORT_BY_NAME name = (PIMAGE_IMPORT_BY_NAME)image_rva_to_va(nt, buffer, thunk->u1.AddressOfData);
                    if (name != NULL) {
                        const char *import_name = (const char *)name->Name;
                        DWORD slot = nt->OptionalHeader.ImageBase + first_thunk;

                        if (strcmp(import_name, "CreateProcessA") == 0) {
                            slots->create_process_slot = slot;
                        } else if (strcmp(import_name, "OpenProcess") == 0) {
                            slots->open_process_slot = slot;
                        } else if (strcmp(import_name, "WriteProcessMemory") == 0) {
                            slots->write_process_memory_slot = slot;
                        }
                    }
                }

                thunk += 1;
                first_thunk += sizeof(IMAGE_THUNK_DATA32);
            }
        }

        descriptor += 1;
    }

    return slots->create_process_slot != 0 && slots->write_process_memory_slot != 0;
}

static int read_remote(HANDLE process, LPCVOID address, void *buffer, SIZE_T size) {
    SIZE_T read_count = 0;
    return ReadProcessMemory(process, address, buffer, size, &read_count) && read_count == size;
}

static int write_remote(HANDLE process, LPVOID address, const void *buffer, SIZE_T size) {
    SIZE_T written = 0;
    return WriteProcessMemory(process, address, buffer, size, &written) && written == size;
}

static int read_remote_string(HANDLE process, DWORD remote_ptr, char *buffer, size_t size) {
    size_t offset = 0;

    if (remote_ptr == 0 || size == 0) {
        if (size != 0) {
            buffer[0] = '\0';
        }
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

static int is_absolute_windows_path(const char *path) {
    if (path[0] == '\\' && path[1] == '\\') {
        return 1;
    }
    if (((path[0] >= 'A' && path[0] <= 'Z') || (path[0] >= 'a' && path[0] <= 'z')) && path[1] == ':') {
        return 1;
    }
    return 0;
}

static void parse_command_target(const char *command_line, char *buffer, size_t size) {
    const char *start = command_line;
    const char *end;
    size_t len;

    while (*start == ' ' || *start == '\t') {
        start += 1;
    }

    if (*start == '"') {
        start += 1;
        end = strchr(start, '"');
        if (end == NULL) {
            end = start + strlen(start);
        }
    } else {
        end = start;
        while (*end != '\0' && *end != ' ' && *end != '\t') {
            end += 1;
        }
    }

    len = (size_t)(end - start);
    if (len >= size) {
        len = size - 1;
    }
    memcpy(buffer, start, len);
    buffer[len] = '\0';
}

static int resolve_child_path(const char *wrapper_dir, const char *application_name, const char *command_line, char *buffer, size_t size) {
    char target[MAX_PATH];

    target[0] = '\0';
    if (application_name != NULL && application_name[0] != '\0') {
        strncpy(target, application_name, sizeof(target) - 1);
        target[sizeof(target) - 1] = '\0';
    } else if (command_line != NULL && command_line[0] != '\0') {
        parse_command_target(command_line, target, sizeof(target));
    }

    if (target[0] == '\0') {
        return 0;
    }

    if (is_absolute_windows_path(target)) {
        strncpy(buffer, target, size - 1);
        buffer[size - 1] = '\0';
        return 1;
    }

    _snprintf(buffer, size, "%s\\%s", wrapper_dir, target);
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

static int patch_child_file(const char *child_path, const char *output_path, DWORD remote_base_address, const BYTE *decrypted, DWORD decrypted_size) {
    BYTE *buffer = NULL;
    DWORD size = 0;
    PIMAGE_NT_HEADERS nt;
    DWORD rva;
    BYTE *target;
    DWORD offset;
    int ok = 0;

    if (!read_file_bytes(child_path, &buffer, &size)) {
        fail("unable to read encrypted child file");
        return 0;
    }

    nt = pe_nt_headers(buffer);
    if (nt == NULL) {
        fail("encrypted child is not a valid PE file");
        goto cleanup;
    }

    if (remote_base_address < nt->OptionalHeader.ImageBase) {
        fail("captured base address is below image base");
        goto cleanup;
    }

    rva = remote_base_address - nt->OptionalHeader.ImageBase;
    target = (BYTE *)image_rva_to_va(nt, buffer, rva);
    if (target == NULL) {
        fail("unable to map decrypted RVA back into the child file");
        goto cleanup;
    }

    offset = (DWORD)(target - buffer);
    if (offset > size || decrypted_size > size - offset) {
        fail("decrypted payload does not fit inside the child file");
        goto cleanup;
    }

    memcpy(target, decrypted, decrypted_size);
    if (!write_file_bytes(output_path, buffer, size)) {
        fail("unable to write reconstructed child executable");
        goto cleanup;
    }

    ok = 1;

cleanup:
    free(buffer);
    return ok;
}

static int run_capture(CaptureState *state) {
    BYTE *loader = NULL;
    DWORD loader_size = 0;
    ImportSlots slots;
    STARTUPINFOA startup_info;
    PROCESS_INFORMATION process_info;
    DEBUG_EVENT event;
    DWORD resolved_create_process = 0;
    DWORD resolved_open_process = 0;
    DWORD resolved_write_process_memory = 0;
    DWORD current_breakpoint = 0;
    BYTE original_byte = 0;
    DWORD started_at = GetTickCount();
    int first_breakpoint = 1;
    int captured = 0;
    BOOL continue_needed = FALSE;

    if (!read_file_bytes(state->wrapper_path, &loader, &loader_size)) {
        fail("unable to open wrapper executable");
        return 0;
    }

    if (!find_kernel32_import_slots(loader, &slots)) {
        fail("unable to locate CreateProcessA/OpenProcess/WriteProcessMemory imports");
        free(loader);
        return 0;
    }
    free(loader);

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
        fail("unable to launch wrapper under the debugger");
        return 0;
    }

    while (GetTickCount() - started_at < 30000) {
        if (!WaitForDebugEvent(&event, 250)) {
            continue;
        }
        continue_needed = TRUE;

        if (event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT &&
            event.u.Exception.ExceptionRecord.ExceptionCode == EXCEPTION_BREAKPOINT) {
            if (first_breakpoint) {
                first_breakpoint = 0;

                if (!read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)slots.create_process_slot, &resolved_create_process, sizeof(resolved_create_process)) ||
                    !read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)slots.write_process_memory_slot, &resolved_write_process_memory, sizeof(resolved_write_process_memory))) {
                    fail("unable to resolve wrapper imports inside the debuggee");
                    break;
                }

                if (slots.open_process_slot != 0 &&
                    !read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)slots.open_process_slot, &resolved_open_process, sizeof(resolved_open_process))) {
                    resolved_open_process = 0;
                }

                current_breakpoint = resolved_create_process;
                if (!arm_breakpoint(process_info.hProcess, current_breakpoint, &original_byte)) {
                    fail("unable to place breakpoint on CreateProcessA");
                    break;
                }
            } else if ((DWORD)(uintptr_t)event.u.Exception.ExceptionRecord.ExceptionAddress == current_breakpoint) {
                CONTEXT context;

                ZeroMemory(&context, sizeof(context));
                context.ContextFlags = CONTEXT_FULL;
                if (!GetThreadContext(process_info.hThread, &context)) {
                    fail("unable to read wrapper thread context");
                    break;
                }

                context.Eip -= 1;
                if (!SetThreadContext(process_info.hThread, &context)) {
                    fail("unable to rewind wrapper thread context");
                    break;
                }

                if (!restore_breakpoint(process_info.hProcess, current_breakpoint, original_byte)) {
                    fail("unable to restore original wrapper opcode");
                    break;
                }

                if (current_breakpoint == resolved_create_process) {
                    DWORD application_name_ptr = 0;
                    DWORD command_line_ptr = 0;
                    char application_name[MAX_PATH];
                    char command_line[MAX_TEXT];

                    application_name[0] = '\0';
                    command_line[0] = '\0';
                    if (!read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)(context.Esp + 4), &application_name_ptr, sizeof(application_name_ptr)) ||
                        !read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)(context.Esp + 8), &command_line_ptr, sizeof(command_line_ptr))) {
                        fail("unable to read CreateProcessA arguments");
                        break;
                    }
                    if (!read_remote_string(process_info.hProcess, application_name_ptr, application_name, sizeof(application_name)) ||
                        !read_remote_string(process_info.hProcess, command_line_ptr, command_line, sizeof(command_line))) {
                        fail("unable to read CreateProcessA strings");
                        break;
                    }
                    if (!resolve_child_path(state->wrapper_dir, application_name, command_line, state->child_path, sizeof(state->child_path))) {
                        fail("unable to resolve child executable path");
                        break;
                    }

                    current_breakpoint = resolved_open_process != 0 ? resolved_open_process : resolved_write_process_memory;
                } else if (current_breakpoint == resolved_open_process) {
                    if (!read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)(context.Esp + 12), &state->child_process_id, sizeof(state->child_process_id))) {
                        fail("unable to read OpenProcess arguments");
                        break;
                    }
                    current_breakpoint = resolved_write_process_memory;
                } else if (current_breakpoint == resolved_write_process_memory) {
                    DWORD remote_buffer = 0;

                    if (!read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)(context.Esp + 8), &state->remote_base_address, sizeof(state->remote_base_address)) ||
                        !read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)(context.Esp + 12), &remote_buffer, sizeof(remote_buffer)) ||
                        !read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)(context.Esp + 16), &state->decrypted_size, sizeof(state->decrypted_size))) {
                        fail("unable to read WriteProcessMemory arguments");
                        break;
                    }

                    state->decrypted = (BYTE *)malloc(state->decrypted_size);
                    if (state->decrypted == NULL) {
                        fail("unable to allocate decrypted payload buffer");
                        break;
                    }

                    if (!read_remote(process_info.hProcess, (LPCVOID)(uintptr_t)remote_buffer, state->decrypted, state->decrypted_size)) {
                        fail("unable to read decrypted payload from wrapper memory");
                        break;
                    }

                    captured = 1;
                    continue_needed = FALSE;
                    break;
                }

                if (!arm_breakpoint(process_info.hProcess, current_breakpoint, &original_byte)) {
                    fail("unable to place the next wrapper breakpoint");
                    break;
                }

                if (!ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE)) {
                    fail("unable to continue the wrapper after a breakpoint");
                    break;
                }
                continue_needed = FALSE;
            }
        } else if (event.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT) {
            break;
        }

        if (continue_needed) {
            ContinueDebugEvent(event.dwProcessId, event.dwThreadId, DBG_CONTINUE);
        }
    }

    if (!captured) {
        fail("timed out before the wrapper revealed the decrypted payload");
    }

    if (state->child_process_id != 0) {
        HANDLE child = OpenProcess(PROCESS_TERMINATE, FALSE, state->child_process_id);
        if (child != NULL) {
            TerminateProcess(child, 0);
            CloseHandle(child);
        }
    }

    TerminateProcess(process_info.hProcess, 0);
    CloseHandle(process_info.hThread);
    CloseHandle(process_info.hProcess);
    return captured;
}

static void usage(void) {
    fprintf(stderr, "usage: reflexive_runtime_unwrapper.exe <wrapper.exe> <output.exe>\n");
}

int main(int argc, char **argv) {
    CaptureState state;
    int ok;

    if (argc != 3) {
        usage();
        return 2;
    }

    ZeroMemory(&state, sizeof(state));
    strncpy(state.wrapper_path, argv[1], sizeof(state.wrapper_path) - 1);
    strncpy(state.output_path, argv[2], sizeof(state.output_path) - 1);
    dirname_from_path(state.wrapper_path, state.wrapper_dir, sizeof(state.wrapper_dir));

    ok = run_capture(&state);
    if (!ok) {
        free(state.decrypted);
        return 1;
    }

    if (state.child_path[0] == '\0') {
        fail("wrapper never revealed a child file path");
        free(state.decrypted);
        return 1;
    }

    if (!patch_child_file(state.child_path, state.output_path, state.remote_base_address, state.decrypted, state.decrypted_size)) {
        free(state.decrypted);
        return 1;
    }

    printf("wrapper=%s\n", state.wrapper_path);
    printf("child=%s\n", state.child_path);
    printf("output=%s\n", state.output_path);
    printf("decrypted_size=%lu\n", (unsigned long)state.decrypted_size);

    free(state.decrypted);
    return 0;
}

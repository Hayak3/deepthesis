import subprocess
import tempfile
import os
import shutil
import time

def compile_latex_to_pdf(
    tex_content: str,
    output_pdf_filename: str = "output.pdf",
    latex_compiler: str = "xelatex",
    project_root: str | None = None,
    resource_dirs_to_copy: list[str] | None = None
) -> str | None:
    """
    Compiles LaTeX content to a PDF file using latexmk,
    and copies specified resource directories (like an 'images' directory)
    to the temporary compilation environment.

    Args:
        tex_content (str): The LaTeX content as a string.
        output_pdf_filename (str): The desired name and path for the final PDF file.
                                   If a relative path, it's relative to the current
                                   working directory where this Python script is run.
        latex_compiler (str): The LaTeX engine to use via latexmk
                              (e.g., 'pdflatex', 'xelatex', 'lualatex').
        project_root (str | None): The absolute path to the project's root directory.
                                   Resource directories will be sought relative to this path.
                                   If None, defaults to the current working directory.
        resource_dirs_to_copy (list[str] | None): A list of directory names (e.g., ["images", "data"])
                                                  that are direct children of `project_root` and
                                                  need to be copied into the temporary compilation directory.
                                                  These directories will be available at the top level
                                                  within the temporary compilation environment.

    Returns:
        str | None: The absolute path to the generated PDF if successful, None otherwise.
    """
    if project_root is None:
        project_root = os.getcwd() # Default to current working directory if not specified
    if resource_dirs_to_copy is None:
        resource_dirs_to_copy = []

    # Create a temporary directory for all compilation artifacts
    with tempfile.TemporaryDirectory() as tmpdir:
        base_filename = "temp_document"  # Base name for the .tex file in tmpdir
        tex_file_path_in_tmp = os.path.join(tmpdir, f"{base_filename}.tex")
        pdf_file_path_in_tmp = os.path.join(tmpdir, f"{base_filename}.pdf")
        log_file_path_in_tmp = os.path.join(tmpdir, f"{base_filename}.log")
        # 1. Write the LaTeX content to the temporary .tex file
        try:
            with open(tex_file_path_in_tmp, "w", encoding="utf-8") as f:
                f.write(tex_content)
        except IOError as e:
            print(f"Error writing temporary .tex file: {e}")
            return None

        # 2. Copy specified resource directories (e.g., 'images') into the temporary directory.
        #    This logic is INSIDE the compile_latex_to_pdf function.
        print(f"Preparing to copy resource directories from project root: {project_root}")
        for dir_name_to_copy in resource_dirs_to_copy:
            source_dir_full_path = os.path.join(project_root, dir_name_to_copy)
            # The destination will be tmpdir/dir_name_to_copy (e.g., tmpdir/images)
            print("tmp dir is ", tmpdir)
            destination_dir_full_path_in_tmp = os.path.join(tmpdir, "images")

            print(f"  Copying resource directory: '{source_dir_full_path}' to '{destination_dir_full_path_in_tmp}'")
            if os.path.isdir(source_dir_full_path):
                try:
                    shutil.copytree(source_dir_full_path, destination_dir_full_path_in_tmp)
                    print(f"  Successfully copied resource directory: '{source_dir_full_path}' to '{destination_dir_full_path_in_tmp}'")
                except FileExistsError:
                    print(f"  Warning: Resource destination '{destination_dir_full_path_in_tmp}' already exists. Skipping copy of '{source_dir_full_path}'.")
                except Exception as e:
                    print(f"  Error copying resource directory '{source_dir_full_path}' to '{destination_dir_full_path_in_tmp}': {e}")
                    # Depending on how critical these resources are, you might return None here.
            else:
                print(f"  Warning: Specified resource directory '{source_dir_full_path}' not found or is not a directory. Skipping copy of '{dir_name_to_copy}'.")
        # 3. Construct and execute the latexmk command
        latexmk_command = [
            "latexmk",
            f"-{latex_compiler}",
            "-interaction=nonstopmode",
            "-file-line-error",
            "-output-directory=" + tmpdir,
            "-g",
            "-f",
            f"{base_filename}.tex"
        ]

        print(f"Executing command: {' '.join(latexmk_command)}")
        print(f"Working directory for latexmk: {tmpdir}")

        try:
            process = subprocess.run(
                latexmk_command,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=tmpdir, # Critical: run latexmk in the directory with the .tex file and resources
                check=False
            )
            # if process.returncode != 0:
            #     print("--- LaTeX Compilation FAILED ---")
            #     print(f"latexmk exit code: {process.returncode}")
            #     print("\n--- latexmk STDOUT ---")
            #     print(process.stdout if process.stdout else "No stdout.")
            #     print("\n--- latexmk STDERR ---")
            #     print(process.stderr if process.stderr else "No stderr.")
            #     if os.path.exists(log_file_path_in_tmp):
            #         print(f"\n--- TAIL OF LOG FILE ({log_file_path_in_tmp}) ---")
            #         try:
            #             with open(log_file_path_in_tmp, "r", encoding="utf-8", errors="replace") as log_file:
            #                 log_lines = log_file.readlines()
            #                 for line in log_lines[-50:]: # Print last 50 lines
            #                     print(line, end="")
            #         except IOError as e:
            #             print(f"Error reading log file: {e}")
            #     else:
            #         print("Log file not found.")
            # return None

            if os.path.exists(pdf_file_path_in_tmp):
                final_output_pdf_path = os.path.abspath(output_pdf_filename)
                try:
                    os.makedirs(os.path.dirname(final_output_pdf_path), exist_ok=True)
                    shutil.copy(pdf_file_path_in_tmp, final_output_pdf_path)
                    print(f"--- LaTeX Compilation SUCCESSFUL ---")
                    print(f"PDF generated at: {final_output_pdf_path}")
                    return final_output_pdf_path
                except Exception as e:
                    print(f"Error copying final PDF from '{pdf_file_path_in_tmp}' to '{final_output_pdf_path}': {e}")
                    return None
            else:
                print("--- LaTeX Compilation WARNING ---")
                print("latexmk exited successfully, but the PDF file was not found in the temporary directory.")
                print(f"Expected PDF at: {pdf_file_path_in_tmp}")
                # (Error printing logic as above)
                return None

        except FileNotFoundError:
            print("Error: 'latexmk' command not found.")
            print("Please ensure LaTeX (e.g., TeX Live, MiKTeX) is installed and 'latexmk' is in your system's PATH.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during subprocess execution: {e}")
            return None
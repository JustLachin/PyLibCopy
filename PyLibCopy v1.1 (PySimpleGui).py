import sys
import subprocess
import webbrowser
import PySimpleGUI as sg

def install_library(library_name, install_dir, window):
    """Function to install a library and update the window with progress."""
    command = [sys.executable, "-m", "pip", "install", library_name, "--target", install_dir]
    try:
        # Run the pip install command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Read the process output and update the window
        for line in process.stdout:
            window['-LOG-'].print(line.strip())
            window['-PROGRESS-'].UpdateBar(1)  # Update the progress bar
            window.refresh()
        
        # Get the final return code and stderr output
        result = process.wait()
        _, stderr = process.communicate()
        
        if result == 0:
            return True, "", stderr
        else:
            return False, "", stderr
    except Exception as e:
        return False, "", str(e)

def main():
    """Function to launch the user interface with PySimpleGUI."""
    # Set the theme for PySimpleGUI
    sg.theme('DarkTeal9')
    
    # Create the layout
    layout = [
        [sg.Text('Library Name:'), sg.InputText(key='-LIBRARY-')],
        [sg.Text('Target Directory:'), sg.InputText(key='-DIR-'), sg.FolderBrowse()],
        [sg.Button('Install Library'), sg.Button('Copy Log'), sg.Button('GitHub Repo')],
        [sg.ProgressBar(max_value=1, orientation='h', size=(40, 20), key='-PROGRESS-')],
        [sg.Multiline(size=(60, 20), key='-LOG-', disabled=True)]
    ]

    # Create the window
    window = sg.Window('PyLibCopy', layout)

    # Main event loop
    while True:
        event, values = window.read()

        # Close the window
        if event == sg.WINDOW_CLOSED:
            break

        # When the install button is clicked
        if event == 'Install Library':
            library_name = values['-LIBRARY-']
            install_dir = values['-DIR-']

            if not library_name:
                sg.popup('Please enter the library name.', title='Warning')
                continue

            if not install_dir:
                sg.popup('Please select a target directory.', title='Warning')
                continue

            # Start the library installation process
            window['-LOG-'].print(f"Installing '{library_name}' in '{install_dir}'...")
            window['-PROGRESS-'].UpdateBar(0)  # Reset the progress bar

            # Call the install function and update the window with the results
            success, stdout, stderr = install_library(library_name, install_dir, window)

            # Print the results to the log
            if stdout:
                window['-LOG-'].print(f'STDOUT:\n{stdout}')
            if stderr:
                window['-LOG-'].print(f'STDERR:\n{stderr}')

            # Show a success or error message
            if success:
                sg.popup(f"The library '{library_name}' was installed successfully.", title='Success')
            else:
                sg.popup(f"An error occurred during installation of '{library_name}'.", title='Error')

        # When the "Copy Log" button is clicked
        if event == 'Copy Log':
            log_text = window['-LOG-'].get()
            sg.clipboard_set(log_text)
            sg.popup('Log text copied to clipboard!', title='Success')

        # When the GitHub Repo button is clicked
        if event == 'GitHub Repo':
            webbrowser.open('https://github.com/JustLachin/PyLibCopy')

    # Close the window
    window.close()

if __name__ == '__main__':
    main()

# setup_project.py
import os
import shutil


def create_project_structure():
    # Define the project root directory
    root_dir = ""

    # Define all directories to create
    directories = [
        "hardware",
        "visualization",
        "experiment",
        "utils",
        "data",  # For experimental data output
        "logs"  # For debug/error logs
    ]

    # Create the root directory
    if os.path.exists(root_dir):
        print(f"Directory {root_dir} already exists. Clearing contents...")
        shutil.rmtree(root_dir)
    os.makedirs(root_dir)

    # Create all subdirectories
    for dir_name in directories:
        os.makedirs(os.path.join(root_dir, dir_name))
        # Create __init__.py in each module directory
        if dir_name not in ['data', 'logs']:
            with open(os.path.join(root_dir, dir_name, '__init__.py'), 'w') as f:
                pass

    # Create all the Python files
    files = {
        '': ['main.py'],
        'hardware': ['eye_tracker.py', 'motion_tracker.py', 'synchronizer.py'],
        'visualization': ['real_time_viz.py', 'analysis_viz.py'],
        'experiment': ['trial_manager.py', 'data_logger.py'],
        'utils': ['calibration.py', 'coordinate_sys.py']
    }

    for directory, file_list in files.items():
        for file_name in file_list:
            file_path = os.path.join(root_dir, directory, file_name)
            with open(file_path, 'w') as f:
                f.write('# ' + file_name + '\n')

    # Create requirement.txt
    requirements = [
        'numpy',
        'matplotlib',
        'seaborn',
        'pandas',
        'pupil-labs-realtime-api',
        'mbientlab-metawear',
        'scipy'
    ]

    with open(os.path.join(root_dir, 'requirements.txt'), 'w') as f:
        for req in requirements:
            f.write(req + '\n')

    # Create README.md with basic project info
    readme_content = """# Block Copy Study

A research experiment studying the influence of posture on visual sampling behavior.

## Setup
1. Clone this repository
2. Install requirements: `pip install -r requirements.txt`
3. Connect Pupil Labs Neon and MbientLabs IMUs
4. Run experiment: `python main.py participant_id`

## Project Structure
- hardware/: Device interfaces
- visualization/: Real-time and analysis visualization
- experiment/: Core experimental logic
- utils/: Support utilities
- data/: Experimental data output
- logs/: Debug and error logs
"""

    with open(os.path.join(root_dir, 'README.md'), 'w') as f:
        f.write(readme_content)


if __name__ == "__main__":
    create_project_structure()
    print("Project structure created successfully!")
    print("You can now populate the files with the provided code.")
# main.py
from hardware import NeonEyeTracker, MotionTracker, DataSynchronizer
from visualization import ExperimentVisualizer, DataVisualizer
from experiment import BlockCopyExperiment, DataLogger
from utils import IMUCalibrator, CoordinateTransformer
from experiment.trial_manager import BlockCopyExperiment
from visualization.real_time_viz import ExperimentVisualizer
import argparse


def main():
    parser = argparse.ArgumentParser(description='Block Copy Experiment')
    parser.add_argument('participant_id', type=int, help='Participant ID number')
    parser.add_argument('--output_dir', default='data/', help='Output directory for data files')
    args = parser.parse_args()

    experiment = BlockCopyExperiment(args.participant_id, args.output_dir)
    visualizer = ExperimentVisualizer(experiment)

    try:
        experiment.initialize_hardware()
        visualizer.start()
        experiment.run()
    except Exception as e:
        print(f"Experiment error: {e}")
    finally:
        experiment.cleanup()


if __name__ == "__main__":
    main()
import torch
torch.set_grad_enabled(False)
import math
from dataset import generate_dataset_disk
from module import *
from training import train, test
from plotter import *

import pandas as pd


def run_experiment(loss_func:str, batch_size, num_experiments, nb_epochs=300):
    train_errors = torch.zeros(num_experiments)
    test_errors = torch.zeros(num_experiments)

    for i in range(num_experiments):
        print("experiment: {}/{}".format(i+1, num_experiments))
        # Load the dataset
        train_input, train_label = generate_dataset_disk()
        test_input, test_label = generate_dataset_disk(plot=False)

        model = Sequential(Linear(2, 25), ReLU(),
                    Linear(25,25), ReLU(),
                    Linear(25,25), ReLU(),
                    Linear(25,2), Sigmoid())
        loss_function = Loss(model, fun=loss_func)
        lr = 1e-3

        train(model,
            loss_function,
            train_input, 
            train_label, 
            nb_epochs, 
            lr, 
            batch_size=batch_size, 
            show_plot=False)

        train_error = test(model, train_input, train_label)
        test_error = test(model, test_input, test_label)
        train_errors[i] = train_error
        test_errors[i] = test_error
        print('Train Error: {}%'.format(train_error))
        print('Test Error: {}%'.format(test_error))

    return torch.mean(train_errors), torch.mean(test_errors), torch.std(train_errors), torch.std(test_errors)



def main():
    num_experiments = 10
    losses = ["MSE", "MAE", "CrossEntropy"]
    batch_sizes = [1, 25, 50, 900]
    
    exp_data = {"loss": [],
                "batch_size" : [],
                "nb_epochs": [],
                "train_error_mean": [],
                "train_error_std" : [],
                "test_error_mean": [],
                "test_error_std" : []
                }

    for loss in losses:
        for batch_size in batch_sizes:
            print("\n")
            print("#"*60)
            print("loss used:", loss, " batch size:", batch_size)
            if batch_size == 900:
                nb_epochs = 600 # with higher batch size we would have less updates
            else:
                nb_epochs = 300
            (train_error_mean, test_error_mean,
                train_error_std, test_error_std) = run_experiment(loss, batch_size, num_experiments, nb_epochs)

            exp_data["loss"].append(loss)
            exp_data["batch_size"].append(batch_size)
            exp_data["nb_epochs"].append(nb_epochs)
            exp_data["train_error_mean"].append(train_error_mean.numpy())
            exp_data["test_error_mean"].append(test_error_mean.numpy())
            exp_data["train_error_std"].append(train_error_std.numpy())
            exp_data["test_error_std"].append(test_error_std.numpy())
    
    df = pd.DataFrame(exp_data)
    df.to_csv("experiments.csv")


if __name__ == '__main__':
    main()

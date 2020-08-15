# Reinforcement Learning agent in Wumpus world



## Description

This project implements a Q-Learning agent to solve the Wumpus World game with a noisy action model. It is built on top of 'The Hunt The Wumpus AI project' developed by Clay Morrison (University of Arizona). Thus the project supports both the Hybrid Logic Agent and Reinforcement learning agent based on Q-Learning to solve the Wumpus World game to compare the merits and demerits of both the approaches.

## Tools Used

This project utilizes the below tools:

* [Python 2.7.2] - A Declarative Programming Language for implementing the compiler and runtime environment.

## Installation

1) This project requires Python 2.7.2 to run. Download it from the below link:

```sh
https://www.python.org/downloads/release/python-272/
```

2) Download the code from the repository:
```sh
$ git clone https://github.com/CSE-571-Team/CSE-571-Spring-2020-Group-10.git
```

## Run Instructions

1) Running the Hybrid Logic Agent:

(i) Using default layout:
```
$ python wumpus.py -y
```

(ii) Using custom layout defined in CSE-571-Spring-2020-Group-10.git/wumpus/layout folder:
```
$ python wumpus.py -y -l wumpus_4x4_1
```

2) Running the Q-Learning Agent with noisy action model:

(i) Using default layout:
```
$ python wumpus.py -q
```

(ii) Using custom layout defined in CSE-571-Spring-2020-Group-10.git/wumpus/layout folder:
```
$ python wumpus.py -q -l wumpus_4x4_1
```



## Learning parameters

Example run:

```
$ python wumpus.py -q -s [0.1,0.8,0.1] -g 0.8 -a 0.2 -e 0.05 -x 12000 -m 2000 -d 0.001 -r 100
```

Parameter details:

```
-s specifies stochasticity with stochastic parameters [0.1,0.8,0.1]. If agent tries to move forward, it will move in the forward location with probability 0.8 and with probability 0.1 in the left and right location respectively. While       specifying this in the parameter, there should be no space inside the square brackets.

-g represents the discount factor (gamma)

-a represents the learning rate (alpha)

-e represents the exploration factor (epsilon)

-x represents the maximum number of training agent receives. Agent will stop after training after it reaches this value even if does not reach the convergence 

-m represents the minimum number of training agent receives before it starts checking for convergence

-d represents the maximum deviation in the Q value. The agent will compare the previous Q values with the current updated Q values for all actions it performs in the environment for a given episode. If all Q value updates are less, than agent will compare the previous policy with the current policy. If both policies match then agent will stop its training

-r represents the number of runs agent will perform after the policy has been generated. Average score after running this many runs by the agent will be printed
```

The below default values will be assumed if the above options are not provided:

```
Stoishasticity (-s): [0.1,0.8,0.1]
Gamma (-g): 0.8
Alpha (-a): 0.2
Epsilon (-e): 0.05
Minimum training (-m): 2000
Minimum training (-x): 12000
Delta (-d): 0.001
Number of runs (-r): 100
```


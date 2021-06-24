# AI Invaders

AI invaders is an AI that plays the game space invaders without human interaction while achieving better than average human performance

## Introduction

AI invaders uses a reinforcement learning algorithm known as Double Deep Q Network (DDQN) with Prioritized Replay an improvement over the Vanilla DQN architecture.

It’s the expected sum of discounted rewards for taking an action in a given state, for a given policy. As given below:

### **Q(s,a)→r+γ maxaQ(s′,a)**

You can find a short video of the trained agent in the folder submitted. – Trained Agent Gameplay.mp4

## Installation

There are two ways to run the application

1. Training mode
2. Play/Test mode
3. Human mode

For both, start with the following steps

```bash
git clone https://github.com/updatesvc/AI-Invaders.git
```

- Requires python with jupyter installed
- Required libraries to install tensorflow, keras, pygame, gym

## 1. Train Mode

Open the “Agent training notebook” in jupyter and run it.
It will periodically save the model’s weights in a file

## 2. Play/Test Mode

Open the “Notebook for running Agent” in jupyter and run it.

To stop the bot, click the stop button of the notebook – due to pygame limitations you can not stop using the X button of the game when testing the trained agent, and to exit completely restart the python kernel or alternatively stop it by exiting jupyter kernel

## 3. Human Mode

To play the game manually (as a human player)

- Open a terminal in the code directory
- Run python play.py

## Additional Details

The trained.h5 contains trained model weights - trained for about 12hrs on colab K80. Reward modelling was difficult, but based on my research the optimal reward model was to limit the amount of bullets, and give a score based on ammo left. Reinforcing accurate and efficient shooting.

## References

Sum Tree from : [Jaromír Janisch](https://github.com/jaromiru/AI-blog/blob/master/SumTree.py)
In depth details on Double DQNs and Prioritised Replay : [Jaromír Janisch Blog](https://jaromiru.com/2016/11/07/lets-make-a-dqn-double-learning-and-prioritized-experience-replay/)

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)

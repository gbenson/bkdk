import gymnasium as gym
import numpy as np
import os
import sys
import tensorflow as tf

from glob import glob
from tensorflow import keras
from tensorflow.keras import layers

from bkdk import TinyScreen


# Configuration paramaters for the whole setup
seed = 186283
gamma = 0.99  # Discount factor for past rewards
epsilon = 1.0  # Epsilon greedy parameter
epsilon_min = 0.1  # Minimum epsilon greedy parameter
epsilon_max = 1.0  # Maximum epsilon greedy parameter
epsilon_interval = (
    epsilon_max - epsilon_min
)  # Rate at which to reduce chance of random action being taken
batch_size = 32  # Size of batch taken from replay buffer
max_steps_per_episode = 10000

checkpoint_prefix = "/home/gary/projects/bkdk/tf-checkpoint-"
restart_checkpoint = None
checkpoints = glob(checkpoint_prefix + "*")
if checkpoints:
    checkpoints = [(int(c.rsplit("-", 1)[-1]), c) for c in checkpoints]
    checkpoints.sort()
    _, restart_checkpoint = checkpoints.pop()
del checkpoints

env = TinyScreen(gym.make("bkdk/BKDK-v0"))
env._window = None
env._clock = None
env.reset(seed=seed)

"""
## Implement the Deep Q-Network

This network learns an approximation of the Q-table, which is a mapping between
the states and actions that an agent will take. For every state we'll have four
actions, that can be taken. The environment provides the state, and the action
is chosen by selecting the larger of the four Q-values predicted in the output layer.

"""

num_actions = env.action_space.n


def create_q_model():
    input_shape = env.observation_space.shape
    if len(input_shape) == 2:
        input_shape += (1,)
    inputs = layers.Input(shape=input_shape)

    # Convolutions on the frames on the screen
    layer1 = layers.Conv2D(32, 3, strides=1, activation="relu")(inputs)
    layer2 = layers.Conv2D(64, 3, strides=1, activation="relu")(layer1)
    layer3 = layers.Conv2D(64, 3, strides=1, activation="relu")(layer2)

    layer4 = layers.Flatten()(layer3)

    layer5 = layers.Dense(512, activation="relu")(layer4)
    action = layers.Dense(num_actions, activation="linear")(layer5)

    return keras.Model(inputs=inputs, outputs=action)


# The first model makes the predictions for Q-values which are used to
# make a action.
model = create_q_model()
# Build a target model for the prediction of future rewards.
# The weights of a target model get updated every 10000 steps thus when the
# loss between the Q-values is calculated the target Q-value is stable.
if restart_checkpoint is None:
    model_target = create_q_model()
    frame_count = 0
    assert False  # XXX don't restart!
else:
    frame_count = int(restart_checkpoint[len(checkpoint_prefix):])
    print(f"Restarting at frame_count = {frame_count}")
    model_target = keras.models.load_model(restart_checkpoint,
                                           compile=False)
    model.set_weights(model_target.get_weights())


"""
## Train
"""
# In the Deepmind paper they use RMSProp however then Adam optimizer
# improves training time
optimizer = keras.optimizers.Adam(learning_rate=0.00025, clipnorm=1.0)

# Experience replay buffers
action_history = []
state_history = []
state_next_history = []
rewards_history = []
done_history = []
episode_reward_history = []
running_reward = 0
episode_count = 0
# Number of frames to take random action and observe output
epsilon_random_frames = 50000
# Number of frames for exploration
epsilon_greedy_frames = 1000000.0
# Maximum replay length
# Note: The Deepmind paper suggests 1000000 however this causes memory issues
max_memory_length = 100000
# Train the model after 4 actions
update_after_actions = 4
# How often to update the target network
update_target_network = 10000
# Using huber loss for stability
loss_function = keras.losses.Huber()

while True:  # Run until solved
    state, info = env.reset()
    state = np.array(state)
    episode_reward = 0
    zero_reward_run = 0

    for timestep in range(1, max_steps_per_episode):
        frame_count += 1

        # Use epsilon-greedy for exploration
        if frame_count < epsilon_random_frames or epsilon > np.random.rand(1)[0]:
            # Take random action
            action = np.random.choice(num_actions)
        elif zero_reward_run > num_actions:
            # Choose a random *valid* action
            print(f" breaking zero-reward run")
            valid_actions = [action
                             for action in range(num_actions)
                             if env.is_valid_action(action)]
            action = np.random.choice(valid_actions)
        else:
            # Predict action Q-values
            # From environment state
            state_tensor = tf.convert_to_tensor(state)
            state_tensor = tf.expand_dims(state_tensor, 0)
            action_probs = model(state_tensor, training=False)
            # Take best action
            action = tf.argmax(action_probs[0]).numpy()

        # Decay probability of taking random action
        epsilon -= epsilon_interval / epsilon_greedy_frames
        epsilon = max(epsilon, epsilon_min)

        # Apply the sampled action in our environment
        state_next, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        if done:
            print(f" final score was {info['score']}")
        state_next = np.array(state_next)

        episode_reward += reward
        if reward == 0:
            zero_reward_run += 1
        else:
            zero_reward_run = 0

        # Save actions and states in replay buffer
        action_history.append(action)
        state_history.append(state)
        state_next_history.append(state_next)
        done_history.append(done)
        rewards_history.append(reward)
        state = state_next

        # Update every fourth frame and once batch size is over 32
        if frame_count % update_after_actions == 0 and len(done_history) > batch_size:

            # Get indices of samples for replay buffers
            indices = np.random.choice(range(len(done_history)), size=batch_size)

            # Using list comprehension to sample from replay buffer
            state_sample = np.array([state_history[i] for i in indices])
            state_next_sample = np.array([state_next_history[i] for i in indices])
            rewards_sample = [rewards_history[i] for i in indices]
            action_sample = [action_history[i] for i in indices]
            done_sample = tf.convert_to_tensor(
                [float(done_history[i]) for i in indices]
            )

            # Build the updated Q-values for the sampled future states
            # Use the target model for stability
            future_rewards = model_target.predict(state_next_sample)
            # Q value = reward + discount factor * expected future reward
            updated_q_values = rewards_sample + gamma * tf.reduce_max(
                future_rewards, axis=1
            )

            # If final frame set the last value to -1
            updated_q_values = updated_q_values * (1 - done_sample) - done_sample

            # Create a mask so we only calculate loss on the updated Q-values
            masks = tf.one_hot(action_sample, num_actions)

            env._render_pygame("human")
            with tf.GradientTape() as tape:
                # Train the model on the states and updated Q-values
                q_values = model(state_sample)

                # Apply the masks to the Q-values to get the Q-value for action taken
                q_action = tf.reduce_sum(tf.multiply(q_values, masks), axis=1)
                # Calculate loss between new Q-value and old Q-value
                loss = loss_function(updated_q_values, q_action)

            # Backpropagation
            grads = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))

        if frame_count % update_target_network == 0:
            # update the the target network with new weights
            model_target.set_weights(model.get_weights())
            # Log details
            template = "running reward: {:.2f} at episode {}, frame count {}"
            print(template.format(running_reward, episode_count, frame_count))
            model_target.save(
                f"{checkpoint_prefix}{frame_count}",
                overwrite=True)
            # restart from checkpoint to work around memory leak
            # XXX or is it just the huge buffers? FIXME!
            sys.stdout.flush()
            sys.stderr.flush()
            os.execl(sys.executable,
                     os.path.basename(sys.executable),
                     *sys.argv)

        # Limit the state and reward history
        if len(rewards_history) > max_memory_length:
            del rewards_history[:1]
            del state_history[:1]
            del state_next_history[:1]
            del action_history[:1]
            del done_history[:1]

        if done:
            break

    # Update running reward to check condition for solving
    episode_reward_history.append(episode_reward)
    if len(episode_reward_history) > 100:
        del episode_reward_history[:1]
    running_reward = np.mean(episode_reward_history)

    episode_count += 1

    if running_reward > 11217:  # Condition to consider the task solved
        print("Solved at episode {}!".format(episode_count))
        break

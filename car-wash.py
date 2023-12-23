# %% [markdown]
# # Car Wash Simulation
# 

# %% [markdown]
# ### The queue of customers
# 
# All we really need to know about the customers is how long they wait in the
# queue. So, when one arrives, we will represent them by a number called a
# *timestamp*. The simulation works in seconds, so the timestamp will just be the
# number of seconds that have already passed during the simulation before the
# customer arrives. When a customer is removed from the queue (their car is
# washed), we can then calculate the number of seconds they waited.

# %%
from collections import deque

# %% [markdown]
# ### The `washer` object
# 
# Instances of the `washer` class simulate the machine that washes cars. Its
# constructor will take one parameter (in addition to `self`): the number of
# seconds needed to wash a car, `wash_time`. When the washer starts washing,
# sets its `time_until_done` attribute equal to `wash_time`.
# 
# Each time another second passes, the simulation program will indicate the
# passage of one second for the washer. This is done by the instance method
# `washer.one_second()`.
# 
# The washer needs to be able to tell the rest of the program whether it is
# currently busy, and to start washing the next car in the queue. These are
# done via member functions `washer.is_busy()` and `washer.wash()`.

# %%
class Washer:
    """The washer knows whether it is washing, and if it is, how long it will be until the
    next car can exit the waiting queue.
    """
    def __init__(self, wash_time):
        """Sets up a Washer instance. Make sure you know what the instance attributes should be!"""
        
        self.wash_time = wash_time
        self.time_until_done = 0

    def is_busy(self):
        """Return True if the washer is currently washing (so no car can
        exit the queue yet) and False if not (the next car can be dequeued)."""
        
        if self.time_until_done != 0:
            return True
        else:
            return False

    def start_washing(self):
        """Tell the washer to wash the car at the front of the
        queue by updating its attributes appropriately."""
        
        if self.is_busy() == False:
            self.time_until_done = self.wash_time

    def one_second(self):
        """Update the washer's attributes to reflect the passage of one second."""
        
        if self.time_until_done != 0:
            self.time_until_done = self.time_until_done - 1

# %%
# Check that the Washer class does what it is supposed to:
from nose.tools import assert_equal
w = Washer(100)
assert_equal(w.wash_time, 100)
assert_equal(w.time_until_done, 0)
for key in vars(w):
    assert(key in ('wash_time', 'time_until_done'))

w.time_until_done = 1
assert(w.is_busy())
w.time_until_done = 0
assert(not w.is_busy())

w.start_washing()
assert_equal(w.time_until_done, w.wash_time)

w.time_until_done = 10
w.one_second()
assert_equal(w.time_until_done, 9)

# %% [markdown]
# ### Managing arrivals
# 
# We'll use the probability input to determine, during each simulated second,
# whether or not a new customer arrives at the rear of the queue. This could be
# done with a simple free-standing (i.e., not an instance method) function, but
# the design choice here is to use a single instance of a custom class, called
# `ArrivalGenerator`. The `ArrivalGenerator` class has a constructor that takes
# one optional argument, the probability input of the program. (If no argument is
# passed, the constructor uses the default value of `0.5`.) It has a single
# instance method `ArrivalGenerator.query()` that returns either `True` or
# `False`, with `True` occurring with probability given by the constructor's
# argument. We'll use some helper functions from the `random` module to generate
# these random occurrences.

# %%
import random

class ArrivalGenerator:
    def __init__(self, prob=0.5):
        """The ArrivalGenerator has one job: return True with probability `prob`.
        To do that, it needs to save the value of `prob`.
        """
        
        self.probability = prob

    def query(self):
        """Return True with probability prob. There are many different ways 
        you might use the `random` module's functions
        to do it. If you want a hint, please ask, I don't want you to get hung up on the
        math of probability too much."""
        
        while self.probability >= random.random():
            return True


# %%
# Check that ArrivalGenerator does what it is supposed to do:
from nose.tools import assert_equal
a = ArrivalGenerator()
assert_equal(a.probability, 0.5)
a = ArrivalGenerator(0.9)
assert_equal(a.probability, 0.9)

arrivals_list = (a.query() for _ in range(1_000_000))
number_of_arrivals = sum([1 for x in arrivals_list if x])
# You should get something very close to 900000
assert(899000 < number_of_arrivals and number_of_arrivals < 901000)
# If it fails, but you think you are right, just try again. It is probabilistic,
# so could be false negative. But two false negatives is unlikely to happen.

# %% [markdown]
# ### Tracking the average waiting time
# 
# To track the average waiting time, we'll use another custom class instance.
# The class is called `AverageTracker`. Its only job is to compute the
# average of a sequence of numbers. For example, we could send the values
# 234, 234, 908, and 279 into an `AverageTracker`. It could then tell us
# that the average of these values is 413.75. It could also tell us that
# so far it has processed 4 values. Thus we can use our `AverageTracker`
# to keep track of the average waiting time *and* the number of customers
# served during the simulation.
# 
# The `AverageTracker` has a constructor that prepares the `AverageTracker`
# instance to accept a sequence of numbers. The instance receives one value
# at a time through instance method `AverageTracker.next_value()`.
# 
# There are two instance methods to obtain info from the `AverageTracker`.
# These are `AverageTracker.number_of_values()` and `AverageTracker.average()`.

# %%
class AverageTracker:
    def __init__(self):
        """The average tracker just needs to know the total of all numbers
        it has received so far and how many numbers it's received."""
        
        self.count = 0
        self.sum_ = 0

    def next_value(self, val):
        """This method adds `val` to the total received so far and increments
        the number of values received."""
        
        self.sum_ += val
        self.count += 1

    def average(self):
        """Return the average of all the values so far."""
        
        return self.sum_ / self.count

    def number_of_values(self):
        """Return the number of values received so far."""
        
        return self.count

# %%
from nose.tools import assert_equal
import random
at = AverageTracker()
assert_equal(at.count, 0)
assert_equal(at.sum_, 0)
for key in vars(at):
    assert(key in ('count', 'sum_'))

at = AverageTracker()
random_value_list = [random.random() for _ in range(1000)]
for val in random_value_list:
    at.next_value(val)

assert_equal(at.count, len(random_value_list))
assert_equal(at.sum_, sum(random_value_list))
assert(at.average() == sum(random_value_list)/len(random_value_list))

# %% [markdown]
# ### Pseudocode for main program
# 
# <ol style="list-style-type: upper-roman">
#     <li>Initialize the input values for the program. These are arrival probability and simulation time.</li>
#     <li>Initialize a <tt>Washer</tt> instance, making sure to supply a value for its parameter (how long it takes to wash a car).</li>
#     <li>Initialize instances of <tt>ArrivalGenerator</tt>, <tt>AverageTracker</tt>, and <tt>deque</tt>.</li>
#     <li>For each integer between 0 and the simulation time:</li>
#     <ol style="list-style-type: upper-alpha">
#         <li>Ask the <tt>ArrivalGenerator</tt> whether a new customer arrives during the current second. If so, enqueue the value of the current second.</li>
#         <li>If the <tt>Washer</tt> is not busy and the queue is not empty:</li>
#         <ol style="list-style-type: arabic">
#             <li>Remove the next value from the queue. This is the arrival timestamp of the car about to get washed.</li>
#             <li>Compute how long the next car had to wait, and send that value to the <tt>AverageTracker</tt>.</li>
#             <li>Tell the <tt>Washer</tt> to start washing the next car in line.</li>
#         </ol>
#             <li>Tell the <tt>Washer</tt> another second has passed. (This is how the washer knows when it is no longer busy.)</li>
#     </ol>
#     <li>Now the simulation is done. Print a report including the simulation time and probability, number of cars washed, and average waiting time. Example:<br/>
#         <tt>Simulation complete<br/>
#         In 1000 seconds with probability 0.005: washed 23 cars with average waiting time 83.2 seconds.
#         </tt>
#     </li>
# </ol>
# 
# ### Read this carefully
# 
# Make sure you don't reinvent the wheel. A fully object-oriented, encapsulated style means that your main program does less work on its own. In this program, it should mostly coordinate the actions of various objects, who handle the details of the simulation as you've already written them. It does this by passing messages (values) between them. Set your objects up, then let them do their work.
# 
# ### Testing your simulation
# 
# You should get realistic values with the probability, simulation time, and wash time that are provided.

# %%
from collections import deque

prob = 0.004
simulation_time = 6000
wash_time = 150

def simulation(prob, simulation_time, wash_time):
    ws = Washer(wash_time)
    arg = ArrivalGenerator(prob)
    avg_wash_time = AverageTracker()
    wash_deque = deque()
    for current_second in range(simulation_time):
        if arg.query() == True:
            wash_deque.appendleft(current_second)
        if ws.is_busy() == False and len(wash_deque) != 0:
            timestamp = wash_deque.pop()
            avg_wash_time.next_value(current_second - timestamp)
            ws.start_washing()
        ws.one_second()
    avg_time = avg_wash_time.average()
    count = avg_wash_time.number_of_values()
    print(f"In {simulation_time} seconds with probability {prob}: washed {count} cars with average waiting time {avg_time} seconds.")
    return count, avg_time

# %% [markdown]
# ### SIMULATE
# 
# Run your simulation ten thousand times (it will take a minute or two). Store the
# results in two lists. Each run of the simulation produces a count and an
# average. After each run, capture these values. Append the count to the list of
# counts and the average to the list of averages. Return the two lists at once,
# like this:
# 
# ```python
# return counts, averages
# ```

# %%
def ten_thousand_runs():
    """
    Get lists of ten thousand counts and averages from the simulator.
    Return the lists like this:
    return counts, averages
    """
    
    counts = []
    averages = []
    for _ in range(10000):
        count, avg_time = simulation(0.004, 6000, 150)
        counts.append(count)
        averages.append(avg_time)
    return counts, averages

counts, averages = ten_thousand_runs()

# %% [markdown]
# To see a graph of your simulated results, run the next cell.

# %%
import matplotlib.pyplot as plt

plt.style.use('seaborn-whitegrid')
plt.plot(counts, averages, '.', color='black')
plt.xlabel("counts")
plt.ylabel("average wait time")



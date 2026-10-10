import time
import random

class Agent:
    def __init__(self, agent_id, agent_type, speed_factor, quality_score):
        self.agent_id = agent_id
        self.agent_type = agent_type # e.g., "Free", "Paid", "Local"
        self.speed_factor = speed_factor # Lower value means faster processing
        self.quality_score = quality_score # Higher value means better quality
        self.current_task = None
        self.tasks_completed = 0

    def is_available(self):
        return self.current_task is None

    def assign_task(self, task):
        self.current_task = task
        print(f"  Agent {self.agent_id} ({self.agent_type}) assigned Task {task.task_id} (P:{task.priority}, C:{task.complexity})")

    def process_task(self):
        if not self.current_task:
            return None

        # Simulate processing time based on task complexity and agent speed
        processing_time = self.current_task.complexity * self.speed_factor
        time.sleep(processing_time / 10) # Scale down for quick demo

        print(f"  Agent {self.agent_id} finished Task {self.current_task.task_id} in {processing_time:.2f}s (simulated). Quality: {self.quality_score}")
        completed_task = self.current_task
        self.current_task = None
        self.tasks_completed += 1
        return completed_task

class Task:
    def __init__(self, task_id, priority, complexity):
        self.task_id = task_id
        self.priority = priority # 1 (high) to 3 (low)
        self.complexity = complexity # 1 (low) to 5 (high)
        self.assigned_to = None
        self.status = "Pending"

class ReviewTimeGateway:
    def __init__(self, agents):
        self.agents = {agent.agent_id: agent for agent in agents}
        self.pending_tasks = []
        self.completed_tasks = []
        self.unassigned_tasks = []

    def add_task(self, task):
        self.pending_tasks.append(task)
        print(f"Gateway received Task {task.task_id} (Priority: {task.priority}, Complexity: {task.complexity})")

    def assign_and_process_tasks(self):
        # Sort tasks by priority (1=high, 3=low) to prioritize critical tasks
        self.pending_tasks.sort(key=lambda t: t.priority)

        print("\n--- Review Time Gateway: Assigning and Processing Tasks ---")

        # Continue as long as there are tasks to assign or agents are busy
        while self.pending_tasks or any(not agent.is_available() for agent in self.agents.values()):
            # First, process any tasks currently assigned to agents
            for agent in self.agents.values():
                if not agent.is_available():
                    completed_task = agent.process_task()
                    if completed_task:
                        self.completed_tasks.append(completed_task)
                        completed_task.status = "Completed"

            # Then, try to assign new tasks from the pending queue
            tasks_to_requeue = []
            while self.pending_tasks:
                task = self.pending_tasks.pop(0)
                assigned = False

                # Core "Review Time Gateway" logic: Route tasks based on priority to specific agent types
                preferred_agent_type = ""
                if task.priority == 1: # High Priority tasks go to 'Paid' agents (faster, higher quality)
                    preferred_agent_type = "Paid"
                elif task.priority == 2: # Medium Priority tasks go to 'Local' agents (balanced)
                    preferred_agent_type = "Local"
                else: # Low Priority tasks go to 'Free' agents (cost-effective, but slower/lower quality)
                    preferred_agent_type = "Free"

                # Find an available agent of the preferred type
                available_preferred_agents = [a for a in self.agents.values() if a.agent_type == preferred_agent_type and a.is_available()]

                if available_preferred_agents:
                    agent = random.choice(available_preferred_agents)
                    agent.assign_task(task)
                    task.assigned_to = agent.agent_id
                    task.status = "In Progress"
                    assigned = True
                else:
                    # Fallback: If no preferred agent is available, try any available agent to keep workflow moving
                    available_any_agents = [a for a in self.agents.values() if a.is_available()]
                    if available_any_agents:
                        agent = random.choice(available_any_agents)
                        print(f"  No {preferred_agent_type} agent available for Task {task.task_id}. Assigning to any available agent {agent.agent_id} ({agent.agent_type}).")
                        agent.assign_task(task)
                        task.assigned_to = agent.agent_id
                        task.status = "In Progress"
                        assigned = True
                    else:
                        # No agents available at all, re-queue the task for next cycle
                        tasks_to_requeue.append(task)
                        print(f"  No agents available for Task {task.task_id}. Re-queueing.")

            self.pending_tasks.extend(tasks_to_requeue)

            # If no tasks are pending and no agents are busy, we are done
            if not self.pending_tasks and all(agent.is_available() for agent in self.agents.values()):
                break

            # Small delay to simulate time passing and agents finishing tasks
            time.sleep(0.5)

        # Collect any remaining unassigned tasks that couldn't be processed
        self.unassigned_tasks = [t for t in self.pending_tasks if t.status == "Pending"]
        self.pending_tasks = [] # Clear the queue after final pass

        print("\n--- All initial tasks processed or deemed unassignable ---")

# Main simulation setup
agents = [
    Agent("A1", "Paid", 0.5, 95), # Fast, High Quality
    Agent("A2", "Paid", 0.6, 90),
    Agent("B1", "Local", 1.0, 80), # Medium Speed, Medium Quality
    Agent("B2", "Local", 1.1, 75),
    Agent("C1", "Free", 2.0, 60), # Slower, Lower Quality
    Agent("C2", "Free", 2.2, 55),
]

gateway = ReviewTimeGateway(agents)

# Create some tasks with varying priorities and complexities
gateway.add_task(Task("T1", 1, 4)) # High Priority, High Complexity -> Prefers Paid
gateway.add_task(Task("T2", 3, 2)) # Low Priority, Low Complexity -> Prefers Free
gateway.add_task(Task("T3", 2, 3)) # Medium Priority, Medium Complexity -> Prefers Local
gateway.add_task(Task("T4", 1, 5)) # High Priority, Very High Complexity -> Prefers Paid
gateway.add_task(Task("T5", 3, 3)) # Low Priority, Medium Complexity -> Prefers Free
gateway.add_task(Task("T6", 2, 2)) # Medium Priority, Low Complexity -> Prefers Local
gateway.add_task(Task("T7", 1, 3)) # High Priority, Medium Complexity -> Prefers Paid
gateway.add_task(Task("T8", 3, 1)) # Low Priority, Very Low Complexity -> Prefers Free

gateway.assign_and_process_tasks()

print("\n--- Simulation Results ---")
print("Completed Tasks:")
for task in gateway.completed_tasks:
    print(f"  Task {task.task_id} (P:{task.priority}, C:{task.complexity}): Status={task.status}, Assigned to Agent {task.assigned_to} ({gateway.agents[task.assigned_to].agent_type})")

if gateway.unassigned_tasks:
    print("\nUnassigned Tasks (due to no available agents):")
    for task in gateway.unassigned_tasks:
        print(f"  Task {task.task_id} (P:{task.priority}, C:{task.complexity}): Status={task.status}")

print("\nAgent Performance Summary:")
for agent in agents:
    print(f"  Agent {agent.agent_id} ({agent.agent_type}): Completed {agent.tasks_completed} tasks. Quality Score: {agent.quality_score}")

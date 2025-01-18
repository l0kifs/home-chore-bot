import json
import random


def split_list_to_groups(tasks: list[dict], persons: list[dict]):
    if len(persons) <= 0:
        raise ValueError("Number of persons must be greater than 0")
    
    random.shuffle(persons)
    tasks.sort(key=lambda task: task['complexity'], reverse=True)
    tasks_by_person = [{'person': person, 'tasks': []} for person in persons]
    
    group_sums = [0] * len(persons)
    group_complexities = [0] * len(persons)
    
    for task in tasks:
        min_group_idx = min(
            range(len(persons)),
            key=lambda i: (group_sums[i], group_complexities[i])
        )
        tasks_by_person[min_group_idx]['tasks'].append(task)
        group_sums[min_group_idx] += 1
        group_complexities[min_group_idx] += task['complexity']   
    return tasks_by_person    

# Example usage
data = [
    {'name': 'task1', 'complexity': 3}, 
    {'name': 'task2', 'complexity': 1}, 
    {'name': 'task1', 'complexity': 5}, 
    {'name': 'task1', 'complexity': 2}, 
    {'name': 'task1', 'complexity': 4}, 
    {'name': 'task1', 'complexity': 3}, 
    {'name': 'task1', 'complexity': 2}, 
    {'name': 'task1', 'complexity': 1}, 
    {'name': 'task1', 'complexity': 5}
]
persons = [
    {'id': 1}, 
    {'id': 2}, 
    {'id': 3}
]
result = split_list_to_groups(data, persons)
print(json.dumps(result, indent = 4))
# # Display results
# for i, group in enumerate(result):
#     group_sum = sum(list(d.values())[0] for d in group)
#     print(f"Group {i+1}: {group} = {group_sum}")

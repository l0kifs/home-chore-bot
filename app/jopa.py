import random


def split_list_to_groups(tasks: list[dict], persons: list[dict]):
    if len(persons) <= 0:
        raise ValueError("Number of persons must be greater than 0")
    
    random.shuffle(persons)
    tasks.sort(key=lambda task: task['complexity'], reverse=True)
    tasks_by_person = [{'person': person, 'tasks': []} for person in persons]

    # # Flatten dictionaries into a list of (key, value) pairs
    # items = [(list(d.keys())[0], list(d.values())[0]) for d in list_of_dicts]
    # # Sort items by value in descending order
    # items.sort(key=lambda x: x[1], reverse=True)
    
    # # Initialize groups
    # groups = [[] for _ in range(group_count)]
    # group_sums = [0] * group_count
    # group_sizes = [0] * group_count
    
    # # Distribute items across groups
    # for key, value in items:
    #     # Find the group with the smallest sum; use size as a tie-breaker
    #     min_group_idx = min(
    #         range(group_count),
    #         key=lambda i: (group_sums[i], group_sizes[i])
    #     )
    #     groups[min_group_idx].append({key: value})
    #     group_sums[min_group_idx] += value
    #     group_sizes[min_group_idx] += 1
    
    # return groups

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

# # Display results
# for i, group in enumerate(result):
#     group_sum = sum(list(d.values())[0] for d in group)
#     print(f"Group {i+1}: {group} = {group_sum}")

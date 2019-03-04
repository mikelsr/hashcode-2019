"""
this file contains the genetic algorithm used for solving TSP of
the graph created with main.py
Heavily based on Eric Stoltz's Evolution of a salesman:
A complete genetic algorithm tutorial for Python
"""


from numpy import array
from operator import itemgetter
from pandas import DataFrame
from random import random, sample


scores = []


class Node:
    def __init__(self, index, tags):
        self.index = index
        self.tags = tags

    # cost returns the inverse of the score obtained with two sets of tags
    def cost(self, node):
        if node is self:
            return 0.0
        score = scores[self.index][node.index]
        return 1/score if score != 0 else 2.0  # no score -> biggest cost

    def __str__(self):
        return str(self.index)


class Fitness:
    def __init__(self, route):
        self.cost = 0.0
        self.fitness = 0.0
        self.route = route

    def route_cost(self):
        if self.cost == 0.0:
            path_cost = 0.0
            for i in range(len(self.route)):
                from_node = self.route[i]
                to_node = None
                if i + 1 < len(self.route):
                    to_node = self.route[i+1]
                else:
                    to_node = self.route[0]
                path_cost += from_node.cost(to_node)
            self.cost = path_cost
        return self.cost

    def route_fitness(self):
        if self.fitness == 0.0:
            self.fitness = 1.0 / self.route_cost()
        return self.fitness


def breed(parent1, parent2):
    gene_a = int(random() * len(parent1))
    gene_b = int(random() * len(parent2))

    start_gene = min(gene_a, gene_b)
    end_gene = max(gene_a, gene_b)

    child_p1 = [parent1[i] for i in range(start_gene, end_gene)]
    child_p2 = [i for i in parent2 if i not in child_p1]

    return child_p1 + child_p2


def breed_population(pool, elite_size):
    random_pool = sample(pool, len(pool))
    children = [pool[i] for i in range(elite_size)]
    length = len(pool) - elite_size
    children += [breed(random_pool[i], random_pool[-i]) for i in range(length)]
    return children


def genetic_algorithm(population, size, elite_size, mutation_rate, generations):
    p = new_population(size, population)
    for i in range(generations):
        print("\rGeneration {}".format(i+1), end='')
        p = next_generation(p, elite_size, mutation_rate)
    print()
    best_route_index = rank_routes(p)[0][0]
    return p[best_route_index]


def mating_pool(population, results):
    return [population[results[i]] for i in range(len(results))]


def mutate(individual, mutation_rate):
    for swapped in range(len(individual)):
        if random() < mutation_rate:
            swapping = int(random() * len(individual))
            individual[swapped], individual[swapping] = \
                individual[swapping], individual[swapped]
    return individual


def mutate_population(population, mutation_rate):
    return [mutate(individual, mutation_rate) for individual in population]


def new_population(size, node_list):
    return [new_route(node_list) for _ in range(size)]


def new_route(node_list):
    return sample(node_list, len(node_list))


def next_generation(current_generation, elite_size, mutation_rate):
    ranked_population = rank_routes(current_generation)
    results = select(ranked_population, elite_size)
    pool = mating_pool(current_generation, results)
    children = breed_population(pool, elite_size)
    new_generation = mutate_population(children, mutation_rate)
    return new_generation


def rank_routes(population):
    results = {i: Fitness(population[i]).route_cost()
               for i in range(len(population))}
    return sorted(results.items(), key=itemgetter(1), reverse=True)


def select(ranked_population, elite_size):
    df = DataFrame(array(ranked_population), columns=["Index", "Fitness"])
    df["cum_sum"] = df.Fitness.cumsum()
    df["cum_perc"] = 100*df.cum_sum/df.Fitness.sum()

    results = [population[0] for population in ranked_population]
    for _ in range(len(ranked_population) - elite_size):
        pick = random()*100
        for i in range(len(ranked_population)):
            if pick < df.iat[i, 3]:
                results.append(ranked_population[i][0])
                break
    return results


def set_scores(s):
    global scores
    scores = s

from pyomo.environ import *
from pyomo.opt import SolverFactory
import os
import time 

def read_knapsack_data(filename):
    with open(filename, 'r') as file:
        n, wmax = map(float, file.readline().split())
        
        profits = []
        weights = []
        for line in file:
            v, w = map(float, line.split())
            profits.append(v)
            weights.append(w)
            
    return int(n), int(wmax), profits, weights 

def solve_knapsack(filename):
    n, wmax, profits, weights = read_knapsack_data(filename)
    
    model = ConcreteModel()
    
    model.item_set = RangeSet(1, n)
    
    model.profit_param = Param(model.item_set, initialize=lambda model, i: profits[i - 1])
    model.weight_param = Param(model.item_set, initialize=lambda model, i: weights[i - 1])
    model.wmax = wmax

    model.item_selection = Var(model.item_set, domain=Binary)
    
    model.obj = Objective(expr=sum(model.profit_param[i] * model.item_selection[i] for i in model.item_set), sense=maximize)
    
    model.weight_constraint = Constraint(expr=sum(model.weight_param[i] * model.item_selection[i] for i in model.item_set) <= model.wmax)
    
    solver = SolverFactory('glpk')
    # result = solver.solve(model, tee=True) # recomendo deixar como True se for executar a instância f8
    result = solver.solve(model, tee=False)
    
    if result.solver.status != 'ok':
        print("Problema não foi resolvido corretamente!")
        return None
    
    selected_items = [i for i in model.item_set if model.item_selection[i].value == 1]
    total_profit = sum(model.profit_param[i] for i in selected_items)
    
    formatted_profit = f"{total_profit:.5f}".rstrip('0').rstrip('.')
    print(f"Lucro total: {formatted_profit}")  
    print(f"Itens selecionados: {selected_items}")
    
    return total_profit, selected_items

if __name__ == '__main__':
    instances_folder = os.path.join(os.path.dirname(__file__), 'low-dimensional')
    
    for instance_file in os.listdir(instances_folder):
        if instance_file.endswith('.txt'):  
            filepath = os.path.join(instances_folder, instance_file)
            print(f"\nResolvendo {instance_file}:")
            
            start_time = time.time() 
            solve_knapsack(filepath)
            end_time = time.time()  
            
            elapsed_time = end_time - start_time 
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = int((elapsed_time - int(elapsed_time)) * 1000) 
            print(f"Tempo de execução: {int(hours):02}:{int(minutes):02}:{int(seconds):02}.{milliseconds:03}") 

"""
COBRA FBA Process
"""
from process_bigraph import Process, Step, Composite, process_registry, pf
from process_bigraph import types as core
from cobra.io import read_sbml_model
from library.add_emitter import get_emitter_schema


# define new types
bounds_type = {
    'lower_bound': {'_type': 'float', '_default': -1000.0},
    'upper_bound': {'_type': 'float', '_default': 1000.0},
}
bounds_tree_type = {
    '_type': 'tree[bounds]',  # TODO -- make this a dict, to make it only one level deep
}
sbml_type = {
    '_type': 'string',
    '_check': 'check_sbml',
}


# define new type methods
def check_sbml(value, bindings, types):
    # Do something to check that the value is a valid SBML file
    return True


# register new types
core.type_registry.register('bounds', bounds_type)
core.type_registry.register('sbml', sbml_type)
core.check_registry.register('check_sbml', check_sbml)


class CobraProcess(Process):
    config_schema = {
        'model_file': 'string',
        'default_objective': {
            '_type': 'string',
            '_default': 'BIOMASS_Ecoli_core_w_GAM'
        },
    }

    def __init__(self, config=None):
        super().__init__(config)
        self.model = read_sbml_model(self.config['model_file'])
        self.reactions = self.model.reactions
        self.metabolites = self.model.metabolites
        self.objective = self.model.objective
        self.boundary = self.model.boundary

    def initial_state(self):
        solution = self.model.optimize()
        optimized_fluxes = solution.fluxes

        state = {
            'inputs': {
                'reaction_bounds': {}
            },
            'outputs': {
                'fluxes': {}
            }
        }
        for reaction in self.model.reactions:
            state['inputs']['reaction_bounds'][reaction.id] = {
                'lower_bound': reaction.lower_bound,
                'upper_bound': reaction.upper_bound
            }
            state['outputs']['fluxes'][reaction.id] = optimized_fluxes[reaction.id]
        return state

    def schema(self):
        return {
            'inputs': {
                'model': 'string',  # 'fbamodel',  # TODO -- add an sbml model type
                'reaction_bounds': {  # TODO -- this needs to be a type that can change number of reactions
                    reaction.id: 'bounds' for reaction in self.reactions
                },
                'objective_reaction': {
                    '_type': 'string',
                    '_default': self.config['default_objective'],
                },
            },
            'outputs': {
                'fluxes': {
                    reaction.id: 'float' for reaction in self.reactions
                },
                'objective_value': 'float',
                'reaction_dual_values': {
                    reaction.id: 'float' for reaction in self.reactions
                },
                'metabolite_dual_values': {
                    metabolite.id: 'float' for metabolite in self.metabolites
                },
                'status': 'string',
            }
        }

    def update(self, inputs, interval):

        # set reaction bounds
        reaction_bounds = inputs['reaction_bounds']
        for reaction_id, bounds in reaction_bounds.items():
            self.model.reactions.get_by_id(reaction_id).bounds = (bounds['lower_bound'], bounds['upper_bound'])

        # set objective
        self.model.objective = self.model.reactions.get_by_id(inputs['objective_reaction'])

        # run solver
        solution = self.model.optimize()

        return {
            'fluxes': solution.fluxes.to_dict(),
            'objective_value': solution.objective_value,
            'reaction_dual_values': solution.reduced_costs.to_dict(),
            'metabolite_dual_values': solution.shadow_prices.to_dict(),
            'status': solution.status,
        }


process_registry.register('cobra', CobraProcess)


def test_process():
    emitter_schema = get_emitter_schema(target_path=['fluxes_store'])

    # make the instance
    instance = {
        'fba': {
            '_type': 'process',
            'address': 'local:cobra',
            'config': {
                'model_file': 'models/e_coli_core.xml'
            },
            'inputs': {
                'model': ['model_store'],
                'reaction_bounds': ['reaction_bounds_store'],
                'objective_reaction': ['objective_reaction_store'],
            },
            'outputs': {
                'fluxes': ['fluxes_store'],
                'objective_value': ['objective_value_store'],
                'reaction_dual_values': ['reaction_dual_values_store'],
                'metabolite_dual_values': ['metabolite_dual_values_store'],
            }
        },
        # insert emitter schema
        **emitter_schema
    }

    # make the composite
    workflow = Composite({'state': instance})

    # run
    workflow.run(1)

    # gather results
    results = workflow.gather_results()
    print(f'RESULTS: {pf(results)}')


if __name__ == '__main__':
    test_process()
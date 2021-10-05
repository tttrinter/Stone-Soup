from base import RunManager
import numpy as np
import itertools

class InputManager(RunManager):

    def set_stateVector(self, list_state_vector):
        """Get a list and return a state vector

        Parameters:
            list_state_vector: State vector list

        Returns:
            StateVector: state vector 
        """
        for idx, elem in enumerate(list_state_vector):
            list_state_vector[idx]=list(elem)
            list_state_vector[idx]=np.c_[list_state_vector[idx]]
        
        return list(list_state_vector)


    def set_int(self, input_int):
        input_int=int(input_int)
        return input_int
    
    def set_float(self, input_float):
        input_float=int(input_float)
        return input_float

    def set_covariance(self, covar):
        covar=np.array(covar)
        print(type(covar))
        return covar

    def set_bool():
        raise NotImplementedError

    def set_tuple():
        raise NotImplementedError

    def set_ndArray():
        raise NotImplementedError

    def set_timeDelta():
        raise NotImplementedError
    
    def set_deltaTime():
        raise NotImplementedError

    def set_coordinate_system():
        raise NotImplementedError

    def set_probability():
        raise NotImplementedError

    def generate_parameters_combinations(self, parameters):
        """[summary]
        From a list of parameters with, min, max and n_samples values generate all the possible values

        Args:
            parameters ([type]): [list of parameters used to calculate all the possible parameters]

        Returns:
            [dict]: [dictionary of all the combinations]
        """
        combination_dict = {}
        combo_list = {}
        int_list = {}
        float_list = {}
        bool_list = {}
        iters = []

        for param in parameters:
            for key, val in param.items():
                path = param["path"]

                if param["type"] == "state_vector" and key == "value_min":
                    for x in range(len(val)):
                        iters.append(self.iterations(param["value_min"][x], param["value_max"][x], param["n_samples"]))
                    combo_list[path] = self.get_trackers_list(iters, param["value_min"])
                    combination_dict.update(combo_list)

                if param["type"] == "int" and key == "value_min":
                    int_iterations = self.iterations(param["value_min"], param["value_max"], param["n_samples"])
                    int_list[path] = [int(x) for x in int_iterations]
                    combination_dict.update(int_list)

                if param["type"] == "float" and key == "value_min":
                    float_iterations = self.iterations(param["value_min"], param["value_max"], param["n_samples"])
                    float_list[path] = [float(x) for x in float_iterations]
                    combination_dict.update(float_list)
                
                if param["type"] == 'bool' and key == "value_min":
                    bool_list[path] = [True, False]
                    combination_dict.update(bool_list)

                if param["type"] == "covar" and key == "value_min":
                    covar=self.set_covariance(val)
                    print(covar.diagonal())     
                    print(covar)     

        return combination_dict

    # Calculate the steps for each item in a list
    def iterations(self, min_value, max_value, num_samples):
        temp = []
        difference = max_value - min_value
        factor = difference / (num_samples - 1)
        for x in range(num_samples):
            temp.append(min_value + (x * factor))
        return temp

    # gets the combinations for one tracker and stores in list
    # Once you have steps created from iterations, generate step combinations for one parameter
    def get_trackers_list(self, iterations_container_list, value_min):
        temp =[]
        for x in range(0, len(value_min)):
            temp.append(iterations_container_list[x])
        list_combinations = list(itertools.product(*temp))
        set_combinations = list(set(list_combinations))
        set_stateVector=self.set_stateVector(set_combinations)
            
        
        return list(set_combinations)

    # Generates all of the combinations between different parameters
    def generate_all_combos(self, trackers_dict):
        """Generates all of the combinations between different parameters

        Args:
            trackers_dict (dict): Dictionary of all the parameters with all the possible values

        Returns:
            dict: Dictionary of all the parameters combined each other
        """
        keys = trackers_dict.keys()
        values = (trackers_dict[key] for key in keys)
        combinations = [dict(zip(keys, combination)) for combination in itertools.product(*values)]
        return combinations
  
""" Tested and developed on python 2.7 and numpy 1.8"""


import csv
import numpy as np




#TODO: What should default behavior be?
#        1: Direct copy of data while compiling a cardinality?
#        2: Raise errors if any of the functions are not re-written?
class Binner(object):
    """ Bass class for binner objects. """
    def __init__(self):
        pass
    def get_cardinality(self):
        pass
    def bin_val(self,value):
        pass 


class OrdinalBinner(Binner):
    """
    Automate the binning of ordinal data into categorical data.  Given
    a list of the upper limits of each bin on init, give access to varaible's
    cardinality through get_cardinality(), and provide bin_val() for the 
    binning of a single value of a variable.
    """
    
    def __init__(self, upper_limits):
        self.upper_limits = upper_limits
        
    def get_cardinality(self):
        return len(self.upper_limits)+1
    
    def bin_val(self, value):
        for i,limit in enumerate(self.upper_limits):
            if value <= limit:
                return i
        return i+1


class TextLengthBinner(OrdinalBinner):
    """
    Used for binning a body of text based on the number of 'words'. bin_val() takes
    a string and splits it into 'words' before returning the binned value.
    Not treating any of the mark-up different from regular text at this point.
    """

    def __init__(self, upper_limits):
        super(TextLengthBinner, self).__init__(upper_limits)

    def bin_val(self,body):
        if not isinstance(body,str):
            raise Exception("TextLengthBinner requires input of type 'str'")
        value = len(body.split())
        return super(TextLengthBinner, self).bin_val(value)


class Dataset(object):
    """ Stuff """
    def __init__(self, frequency_table_csv=None, raw_csv=None,
                 binners=None, raw_variable_names=None):
        """ 
        Import data from file.  Prioritize frequency_table_csv over raw_csv.
        
        If frequency_table_csv is used:
            Expect a header line holding the variable names.

        If raw_csv is used:  
            if raw_csv includes a header, expect raw_variable_names = None.
                else expect raw_variable_names = <list of varaible names>.
            Parameter binners  

        

        Return True if data successfully read, false if not.
        """

        #TODO: Split out data import into import_train_data funciton
        #TODO: Add import_test_data function.
        #TODO: Data imports are to have associated reset functions.  Multiple
        # calls to a data import will import and aggregate many files.
        # Alternatively, is there any use to requrie the train and test sets
        # be two different Datasets?

        # reason for how I handle file non-existence or read failure:
        # https://mail.python.org/pipermail/python-ideas/2009-May/004900.html

            
        try:
            with open(frequency_table_csv,'r') as f:

                expected_width = len(variable_names) + 1
                # TODO; read frequency table
                raise Exception("Import frequency_table_csv not yet written.")

        except:
            try:
                def clean_row(extracted_row, field_types):
                    """
                    Clean the extracted row, casting to the desired type when
                    necessary.
                    """
                    cleaned_row = []
                    for field,ftype in zip(extracted_row,field_types):
                        if isinstance(field,ftype):
                            cleaned = field
                        elif field == '':
                            cleaned = 0
                        else:
                            cleaned = ftype(field)
                        cleaned_row.append(cleaned)
                    return cleaned_row

                with open(raw_csv,'r') as f:
                    reader = csv.reader(f)

                    # raw_variable_names is the list of variables as seen in
                    # the source data.  self.variable_names are the variables
                    # as saved in the object's data structures.
                    
                    # Compile header into variable name list.
                    if raw_variable_names is None:
                        raw_variable_names = reader.next()
                    # else:
                    #     raw_variable_names = raw_variable_names
                    self.variable_names = [val[0] for val in binners]
                    
                    # Initialize frequency matrix
                    card_list = [val[1].get_cardinality() for val in binners]
                    self.frequency_matrix = np.zeros(tuple(card_list),
                                                     dtype='u4')

                    # Populate frequency matrix.
                    var_pointer = [raw_variable_names.index(var)
                                  for var in self.variable_names]
                    field_types = [val[2] for val in binners]
                    expected_length = len(raw_variable_names)
                    for l,row in enumerate(reader):
                        
                        if not expected_length == len(row):
                            for i, item in enumerate(row):
                                print "**%d**"%i,item
                            raise Exception("Invalid row length",
                                            "length: %d"%len(row),
                                            "line number: %d"%l)
                        extracted_row = [row[i] for i in var_pointer]
                        # this breaks when we the value is a non-empty string
                        #cleaned_row = [0 if val == '' else int(val) 
                        #               for val in extracted_row]
                        #using this instead
                        cleaned_row = clean_row(extracted_row, field_types)
                        binned_row = [binners[i][1].bin_val(val) for 
                                      i,val in enumerate(cleaned_row)]
                        self.frequency_matrix[tuple(binned_row)] += 1


            except Exception, e:
                raise e
        self.N = self.frequency_matrix.sum()
        self.probability_matrix = np.array(self.frequency_matrix,
                                           dtype=np.float64,) /self.N
        # self.n_variables = len(self.variable_list)

    def extract_component(self,variable_list):
        """
        Compile subset of Dataset as a frequency matrix (ndarray). Variables
        that remain are given in variable_list.

        *currently only accepts list of ints that are the indices of the 
        desired variables.
        """
        # TODO make buffer that stores a limited number of componets (set 
        # limit on memory or number of components?) to alleviate redundant
        # aggregations.

        if all(isinstance(variable,int) for variable in variable_list):
            pointer_list = variable_list
        elif all(isinstance(variable,str) for variable in variable_list):
            # TODO convert to int
            pointer_list = [self.variable_names.index(var)
                            for var in variable_list]
        else:
            raise Exception("invalid variable_list parmeter in \
                             extract_component.")

        unwanted_variables = [v for v in range(len(self.variable_names)) 
                              if not v in pointer_list]

        # Keep dims so math works out more easily later and to track
        # which variables are aggregated.
        return np.sum(a=self.probability_matrix,
                      axis=tuple(unwanted_variables),
                      keepdims=True)


    def save_frequency_table(self,filename):
        """ save the frequency table as a csv """
        raise Exception("save_frequency_table() not yet written")

    def save_frequency_matrix(self,filename):
        """ save the frequency matrix as a numpy array """
        raise Exception("Function not written.")

    def save_as_occam3_format(self,filename,):
        """ 
        Save the frequency table in an Occam3-readable format.
        *** for now, system is assumed to be undirected without a test set.
        """

        writer = open(filename, 'w')

        #write header
        writer.write(":action\n")
        writer.write("search\n")
        writer.write("\n")

        #write variable info.
        writer.write(":nominal\n")
        for i,cardinality in enumerate(self.frequency_matrix.shape):
            var_letter = chr(i+97)  #"chr(i+97)" 0 is a.  1 is b, etc.

            #TODO: change the third entry (1) to 2 for DVs.
            writer.write("%s, %d, %d, %s \n" % 
                                  (str(i), cardinality, 1, var_letter))

        #write data.
        # http://docs.scipy.org/doc/numpy/reference/arrays.nditer.html#tracking-an-index-or-multi-index
        writer.write("\n")
        writer.write(":data\n")
        it = np.nditer(self.frequency_matrix, flags=['multi_index'])
        while not it.finished:
            writer.write(','.join(map(str,list(it.multi_index) + [it[0]])))
            writer.write('\n')
            it.iternext()



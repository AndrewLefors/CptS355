from colors import *
from psexpressions import StringValue, DictionaryValue, CodeArrayValue

class PSOperators:
    def __init__(self, scoperule):
        #stack variables
        self.opstack = []  #assuming top of the stack is the end of the list
        self.dictstack = [(0, {})]  #assuming top of the stack is the end of the list
        #attrbute for scope rule for static and dynamic scoping
        self.scope = scoperule
        self.builtin_operators = {
            "add":self.add,
            "sub":self.sub,
            "mul":self.mul,
            "mod":self.mod,
            "eq":self.eq,
            "lt": self.lt,
            "gt": self.gt,
            "dup": self.dup,
            "exch":self.exch,
            "pop":self.pop,
            "copy":self.copy,
            "count": self.count,
            "clear":self.clear,
            "stack":self.stack,
            "dict":self.psDict,
            "string":self.string,
            "length":self.length,
            "get":self.get,
            "put":self.put,
            "getinterval":self.getinterval,
            "putinterval":self.putinterval,
            "search" : self.search,
            "def":self.psDef,
            "if":self.psIf,
            "ifelse":self.psIfelse,
            "for":self.psFor
        }
    #------- Operand Stack Helper Functions --------------
    
    """
        Helper function. Pops the top value from opstack and returns it.
    """
    def opPop(self):
        if len(self.opstack) > 0:
            x = self.opstack[len(self.opstack) - 1]
            self.opstack.pop(len(self.opstack) - 1)
            return x
        else:
            print("Error: opPop - Operand stack is empty")

    """
       Helper function. Pushes the given value to the opstack.
    """
    def opPush(self,value):
        self.opstack.append(value)

    #------- Dict Stack Helper Functions --------------
    """
       Helper function. Pops the top dictionary from dictstack and returns it.
    """  
    def dictPop(self):
        if len(self.dictstack) > 0:
            x = self.dictstack[-1]
            self.dictstack.pop(-1)
            return x
        else:
            print("Error: dictPop - Dict stack is empty")

    """
       Helper function. Pushes the given dictionary onto the dictstack. 
    """   
    def dictPush(self,d):
        #var = DictionaryValue(d)
        
        self.dictstack.append(d)
        

    """
       Helper function. Adds name:value pair to the top dictionary in the dictstack.
       (Note: If the dictstack is empty, first adds an empty dictionary to the dictstack then adds the name:value to that. 
    """  
    def define(self, name, value):
        if (name[0] != '/'):
            print("Error: Variable names MUST begin with '/'.")
            return None
        if (len(self.dictstack) > 0):
            # Get the topmost tuple from the dictstack
            static_link_index, varDict = self.dictstack[-1]

            # Update the dictionary with the new variable
            varDict[name] = value

            # No need to pop and push the dictionary, as the update is done in place
        else:
            # If the dictstack is empty, push a new tuple with the base static-link-index and a dictionary with the new variable
            self.dictstack.append((0, {name: value}))



            
    
    """
       Helper function. Searches the dictstack for a variable or function and returns its value. 
       (Starts searching at the top of the dictstack; if name is not found returns None and prints an error message.
        Make sure to add '/' to the begining of the name.)
    """

    def lookup(self, name):
        if len(self.dictstack) > 0:
            if self.scope == "dynamic":
                # Dynamic scoping: search the dictstack from top to bottom
                for i in range(len(self.dictstack) - 1, -1, -1):
                    varDict = self.dictstack[i][1]  # Access the dictionary part of the tuple
                    if ("/" + name) in varDict:
                        return varDict["/" + name]
            else:
                # Static scoping: follow the static links
                index = len(self.dictstack) - 1
                while index >= 0:
                    static_link_index, varDict = self.dictstack[index]
                    if ("/" + name) in varDict:
                        return varDict["/" + name]
                    index = static_link_index

        print("Error: Key not found in Dict!")
        return None

    #------- Arithmetic Operators --------------

    """
       Pops 2 values from opstack; checks if they are numerical (int); adds them; then pushes the result back to opstack. 
    """  
    def add(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            if (isinstance(op1,int) or isinstance(op1,float))  and (isinstance(op2,int) or isinstance(op2,float)):
                self.opPush(op1 + op2)
            else:
                print("Error: add - one of the operands is not a number value")
                self.opPush(op1)
                self.opPush(op2)             
        else:
            print("Error: add expects 2 operands")

    """
       Pops 2 values from opstack; checks if they are numerical (int); subtracts them; and pushes the result back to opstack. 
    """ 
    def sub(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            if (isinstance(op1, int) or isinstance(op1, float)) and (isinstance(op2, int) or isinstance(op2, float)):
                self.opPush(op2 - op1)
            else:
                print("Error: sub - one of the operands is not a number value")

    """
        Pops 2 values from opstack; checks if they are numerical (int); multiplies them; and pushes the result back to opstack. 
    """
    def mul(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            if (isinstance(op1, int) or isinstance(op1, float)) and (isinstance(op2, int) or isinstance(op2, float)):
                self.opPush(op1 * op2)
            else:
                print("Error: mul - one of the operands is not a number value")

    """
        Pops 2 values from stack; checks if they are int values; calculates the remainder of dividing the bottom value by the top one; 
        pushes the result back to opstack.
    """
    def mod(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            if (isinstance(op1, int) or isinstance(op1, float)) and (isinstance(op2, int) or isinstance(op2, float)):
                self.opPush(op2 % op1)
            else:
                print("Error: mod - one of the operands is not a number value")

    """ Pops 2 values from stacks; if they are equal pushes True back onto stack, otherwise it pushes False.
          - if they are integers or booleans, compares their values. 
          - if they are StringValue values, compares the `value` attributes of the StringValue objects;
          - if they are DictionaryValue objects, compares the objects themselves (i.e., ids of the objects).
        """
    def eq(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            var = False
            if (isinstance(op1, int) or isinstance(op1, float)) and (isinstance(op2, int) or isinstance(op2, float)):
                if (op1 == op2):
                    var = True
            elif (isinstance(op1, StringValue) and isinstance(op2, StringValue)):
                if (op1.value == op2.value):
                    var = True
            elif (isinstance(op1, DictionaryValue) and isinstance(op2, DictionaryValue)):
                if (id(op1) == id(op2)):
                    var = True
            else:
                print("Error: eq - one or both operands are of incompatible type")
        self.opPush(var)
        

    """ Pops 2 values from stacks; if the bottom value is less than the second, pushes True back onto stack, otherwise it pushes False.
          - if they are integers or booleans, compares their values. 
          - if they are StringValue values, compares the `value` attributes of them;
          - if they are DictionaryValue objects, compares the objects themselves (i.e., ids of the objects).
    """  
    def lt(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            
            if (isinstance(op1, int) or isinstance(op1, float)) and (isinstance(op2, int) or isinstance(op2, float)):
                if (op2 < op1):
                    var = True
                else:
                    var = False
            elif (isinstance(op1, StringValue) and isinstance(op2, StringValue)):
                if (op2.value < op1.value):
                    var = True
                else:
                    var = False
            elif (isinstance(op1, DictionaryValue) and isinstance(op2, DictionaryValue)):
                if (id(op2) < id(op1)):
                    var = True
                else:
                    var = False
            else:
                print("Error: lt - one or both operands are of incompatible type")
        self.opPush(var)
        


    """ Pops 2 values from stacks; if the bottom value is greater than the second, pushes True back onto stack, otherwise it pushes False.
          - if they are integers or booleans, compares their values. 
          - if they are StringValue values, compares the `value` attributes of them;
          - if they are DictionaryValue objects, compares the objects themselves (i.e., ids of the objects).
    """  
    def gt(self):
        if len(self.opstack) > 1:
            op1 = self.opPop()
            op2 = self.opPop()
            var = False
            if (isinstance(op1, int) or isinstance(op1, float)) and (isinstance(op2, int) or isinstance(op2, float)):
                if (op2 > op1):
                    var = True
            elif (isinstance(op1, StringValue) and isinstance(op2, StringValue)):
                if (op2.value > op1.value):
                    var = True
            elif (isinstance(op1, DictionaryValue) and isinstance(op2, DictionaryValue)):
                if (id(op2) > id(op1)):
                    var = True
            else:
                print("Error: gt - one or both operands are of incompatible type")
        self.opPush(var)


    #------- Stack Manipulation and Print Operators --------------
    """
       This function implements the Postscript "pop operator". Calls self.opPop() to pop the top value from the opstack and discards the value. 
    """
    def pop (self):
        if (len(self.opstack) > 0):
            self.opPop()
        else:
            print("Error: pop - not enough arguments")

    """
       Prints the opstack and dictstack. The end of the list is the top of the stack. 
    """
    def stack(self):
        print(self.scope.upper())
        print("===**opstack**===")
        for item in reversed(self.opstack):
            print(item)
        print("===**dictstack**===")
        for i, item in enumerate(reversed(self.dictstack)):
            static_link_index, item_dict = item
            print("----{}----{}----".format(i, static_link_index))
            for key, value in item_dict.items():
                print("{key} {value}".format(key=key, value=value))
        print("=================")







    """
       Copies the top element in opstack.
    """
    def dup(self):
        if (len(self.opstack) > 0):
            var = self.opstack[-1]
            self.opPush(var)
        else:
            print("Error: dup - opStack is empty!")
        pass

    """
       Pops an integer count from opstack, copies count number of values in the opstack. 
    """
    def copy(self):
        if len(self.opstack) > 0:
            n = self.opPop()
            if isinstance(n, int) and n >= 0:
                if len(self.opstack) >= n:
                    for i in range(len(self.opstack) - n, len(self.opstack)):
                        copyOp = self.opstack[i]
                        if isinstance(copyOp, int):
                            self.opPush(int(copyOp))
                        elif isinstance(copyOp, StringValue):
                            self.opPush(StringValue(copyOp.value))
                        else:
                            raise ValueError("Unsupported object type for deep copy")
                else:
                    raise ValueError("Not enough elements on the stack for copy operation")
            else:
                raise ValueError("Invalid argument for copy operation")
        else:
            raise ValueError("Empty stack for copy operation")


        

    """
        Counts the number of elements in the opstack and pushes the count onto the top of the opstack.
    """
    def count(self):
        var = len(self.opstack)
        self.opPush(var)

    """
       Clears the opstack.
    """
    def clear(self):
        self.opstack.clear()
        
    """
       swaps the top two elements in opstack
    """
    def exch(self):
        if (len(self.opstack) > 1):
            op1 = self.opPop()
            op2 = self.opPop()
            self.opPush(op1)
            self.opPush(op2)
        else:
            print("Error: exch - Not enough operators on opStack to exchange!")

    # ------- String and Dictionary creator operators --------------

    """ Creates a new empty string  pushes it on the opstack.
    Initializes the characters in the new string to \0 , i.e., ascii NUL """
    def string(self):
        if (len(self.opstack) > 0):
            quant = self.opPop()
            
            strVar = ""
            for i in range(0, quant):
                strVar = strVar + '\0'
            var = StringValue( '(' + strVar + ')' )
            self.opPush(var)
    
    """Creates a new empty dictionary  pushes it on the opstack """
    def psDict(self):
        if (len(self.opstack) > 0):
            randVar = self.opPop()
            var = DictionaryValue({})
            self.opPush(var)
        

    # ------- String and Dictionary Operators --------------
    """ Pops a string or dictionary value from the operand stack and calculates the length of it. Pushes the length back onto the stack.
       The `length` method should support both DictionaryValue and StringValue values.
    """
    def length(self):
        if (len(self.opstack) > 0):
            var = self.opPop()
            x = var.length()
            self.opPush(x)


    """ Pops either:
         -  "A (zero-based) index and an StringValue value" from opstack OR 
         -  "A `name` (i.e., a key) and DictionaryValue value" from opstack.  
        If the argument is a StringValue, pushes the ascii value of the the character in the string at the index onto the opstack;
        If the argument is an DictionaryValue, gets the value for the given `name` from DictionaryValue's dictionary value and pushes it onto the opstack
    """
    def get(self):
        if (len(self.opstack) > 1):
            op1 = self.opPop()
            op2 = self.opPop()

            if (isinstance(op2, StringValue)):
                myVal = ord(op2.value[op1+1])
                self.opPush(myVal)
            elif (isinstance(op2, DictionaryValue)):
                self.opPush(op2.value[op1])
            else:
                print("Error: get - Get must be provided an Index and StringValue, or string and DictionaryValue")
        else:
            print("Error: get - Get requires 2 values on the opStack")
        
   
    """
    Pops either:
    - "An `item`, a (zero-based) `index`, and an StringValue value from  opstack", OR
    - "An `item`, a `name`, and a DictionaryValue value from  opstack". 
    If the argument is a StringValue, replaces the character at `index` of the StringValue's string with the character having the ASCII value of `item`.
    If the argument is an DictionaryValue, adds (or updates) "name:item" in DictionaryValue's dictionary `value`.
    """
    def put(self):
        if (len(self.opstack) > 2):
            item = self.opPop()
            indexName = self.opPop()
            value = self.opPop()
            if (isinstance(value, StringValue)):
                value.value = value.value[:indexName+1] + chr(item) + value.value[indexName+2:]
            elif (isinstance(value, DictionaryValue)):
                value.value[indexName] = item
            else:
                print("Error: get - Get must be provided an Index and StringValue, or string and DictionaryValue")
            
        else:
            print("Error: get - Get requires 2 values on the opStack")

    """
    getinterval is a string only operator, i.e., works only with StringValue values. 
    Pops a `count`, a (zero-based) `index`, and an StringValue value from  opstack, and 
    extracts a substring of length count from the `value` of StringValue starting from `index`,
    pushes the substring back to opstack as a StringValue value. 
    """ 
    def getinterval(self):
        count = self.opPop()
        index = self.opPop()
        value = self.opPop()

        if not isinstance(value, StringValue):
            print("Error: getinterval - GetInterval only operates on a StringValue and requires a count and index")
            return

        # Create a new StringValue object containing the substring
        substring = '(' + value.value[index+1:index + count+1] + ')'
        new_string = StringValue(substring)
        print("GET INTERVAL: %s", new_string)
        self.opPush(new_string)



    """
    putinterval is a string only operator, i.e., works only with StringValue values. 
    Pops a StringValue value, a (zero-based) `index`, a `substring` from  opstack, and 
    replaces the slice in StringValue's `value` from `index` to `index`+len(substring)  with the given `substring`s value. 
    """
    def putinterval(self):
        substring = self.opPop()
        index = self.opPop()
        value = self.opPop()
        if substring.value.startswith('('):
            substring.value = substring.value[1:]
        if substring.value.endswith(')'):
            substring.value = substring.value[:-1]
        if (not(isinstance(value, StringValue)) or not(isinstance(substring, StringValue))):
            print("Error: getinterval - GetInterval only operates on a StringValue and requires a count and index")
            return
        value.value = value.value[:index+1] + substring.value + value.value[index+len(substring.value)+1:]
        if not value.value.startswith('('):
            value.value = '(' + value.value
        if not value.value.endswith(')'):
            value.value = value.value + ')'
        print("PUT INTERVAL: ", value.value)


        


    """
    search is a string only operator, i.e., works only with StringValue values. 
    Pops two StringValue values: delimiter and inputstr
    if delimiter is a sub-string of inputstr then, 
       - splits inputstr at the first occurence of delimeter and pushes the splitted strings to opstack as StringValue values;
       - pushes True 
    else,
        - pushes  the original inputstr back to opstack
        - pushes False
    """
    def search(self):
        delimiter = self.opPop()
        inputstr = self.opPop()
        flag = False
        if (not(isinstance(delimiter, StringValue)) and not(isinstance(inputstr, StringValue))):
            print("Error: Input types must be of type StringValue")
            return
        if (delimiter.value[1:-1] in inputstr.value[1:-1]):
            head, tail = inputstr.value[1:-1].split(delimiter.value[1:-1], 1)
            self.opPush(StringValue('('+tail+')'))
            self.opPush(delimiter)
            self.opPush(StringValue('('+ head + ')'))
            flag = True
        else:
            self.opPush(inputstr)
        self.opPush(flag)
           

    # ------- Operators that manipulate the dictstact --------------
        
    """ Pops a name and a value from stack, adds the definition to the dictionary at the top of the dictstack. """
    def psDef(self):
        if (len(self.opstack) > 1):
            value = self.opPop()
            name = self.opPop()
            self.define(name, value)


    # ------- if/ifelse Operators -------------.-
    """ if operator
        Pops a CodeArrayValue object and a boolean value, if the value is True, executes (applies) the code array by calling apply.
       Will be completed in part-2. 
    """
    def psIf(self):
        condition = self.opPop()
        code = self.opPop()

        if not isinstance(condition, bool) or not isinstance(code, CodeArrayValue):
            raise ValueError("Invalid arguments for if operator")

        if condition:
            code.apply(self)
        else:
            self.dictPop()

    """ ifelse operator
        Pops two CodeArrayValue objects and a boolean value, if the value is True, executes (applies) the bottom CodeArrayValue otherwise executes the top CodeArrayValue.
        Will be completed in part-2. 
    """
    def psIfelse(self):
        else_code = self.opPop()
        if_code = self.opPop()
        condition = self.opPop()

        if not isinstance(condition, bool) or not isinstance(if_code, CodeArrayValue) or not isinstance(else_code, CodeArrayValue):
            raise ValueError("Invalid arguments for ifelse operator")

        if condition:
            if_code.apply(self)
        else:
            else_code.apply(self)
        self.dictPop()

        


    #------- Loop Operators --------------
    """
       Implements for operator.   
       Pops a CodeArrayValue object, the end index (end), the increment (inc), and the begin index (begin) and 
       executes the code array for all loop index values ranging from `begin` to `end`. 
       Pushes the current loop index value to opstack before each execution of the CodeArrayValue. 
       Will be completed in part-2. 
    """ 
    def psFor(self):
        code = self.opPop()
        end = self.opPop()
        inc = self.opPop()
        begin = self.opPop()

        if not isinstance(code, CodeArrayValue) or not isinstance(end, int) or not isinstance(inc, int) or not isinstance(begin, int):
            raise ValueError("Invalid arguments for for operator")

        # Add a condition to break out of the loop when `inc` is 0
        if inc == 0:
            raise ValueError("Increment value in for loop cannot be 0")

        # Determine the direction of the loop
        if inc > 0:
            cond = lambda x, y: x <= y
        else:
            cond = lambda x, y: x >= y

        # Execute the loop
        for i in range(begin, end + inc, inc):
            if not cond(i, end):
                break
            self.opPush(i)
            code.apply(self)




    """ Cleans both stacks. """      
    def clearBoth(self):
        self.opstack[:] = []
        self.dictstack[:] = []

    """ Will be needed for part2"""
    def cleanTop(self):
        if len(self.opstack)>1:
            if self.opstack[-1] is None:
                self.opstack.pop()


# Component Specification Parser Task

> General:
> • Treat the code as if it goes to production - apply high coding standards according to your discretion.
> • Make sure the code produces correct results on the attached examples.
> • Don't attempt to use Machine-Learning based models. The task can and should be performed using deterministic code.
> 
> 
> Task:
> • The attached files contain text obtained (in theory, though the decoding might be challenge) from components datasheet.
> • Write a system in Python with the following capabilities:
> Reading the content of all the given components' text files.
> Parsing and storing for each file component the operating voltage range 
> (i.e. the voltages values in which the component can function; e.g. from 5V to 12V) 
> and the operating temperature range i.e. the temperatures in which the component can function (e.g. from -40C to 85C).
> • All files contain at least one range for the each of the items. 
> If a file has more than one range for an item check if they are identical. 
> If they are, use it as the parsed range. If not, write None as the range.
> • Given specific operating conditions return all the components that can operate under these conditions. 
> The conditions are given as two floats, one for the voltage and one for the temperature, 
> and they are assumed to be in the standard units (e.g. 5 for 5V and -20 for -20C).
> This is the interface with which the system is used.
> 
> Add a test file to test the system.
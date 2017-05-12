import salmon.lang as sal 
from salmon.comp import mpc

@mpc
def protocol():

    # define inputs
    colsInA = [
        ("INTEGER", set([1, 2, 3])), 
        ("INTEGER", set([1, 2, 3])), 
        ("INTEGER", set([1, 2, 3]))
    ]
    inA = sal.create("inA", colsInA)

    # specify the workflow
    agg = sal.aggregate(inA, "agg", "inA_0", "inA_1", "+")
    projA = sal.project(agg, "projA", None)
    projB = sal.project(projA, "projB", None)

    # return root nodes
    return set([inA])

if __name__ == "__main__":

    print(protocol())
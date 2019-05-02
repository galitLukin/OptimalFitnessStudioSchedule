using DataFrames, MLDataUtils

include("formulation.jl")
incude("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
#A = 12
L = 10
U = 50

eps = 0
lb = 0
ub = 10000

# A is a vector of uncertainty matrices
A = firstUncertainty()
while ub - lb > eps
    x, lb = getSchedule(A)
    ub, R = worstCase(x,A)
    append(A,R)
end
println(ub)
visualizeSchedule(x)

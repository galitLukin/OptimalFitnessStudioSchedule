using DataFrames, MLDataUtils

include("formulation.jl")
include("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
L = 5
U = 50

eps = 0
lb = 0
ub = 10000

k = 1
# A is a vector of uncertainty matrices
A = firstUncertainty()
# while ub - lb > eps
#     x, lb = getSchedule(A)
#     println("Got schedule $k")
#     ub, R = worstCase(x,A)
#     append(A,R)
#     k = k + 1
# end
println(ub)
visualizeSchedule(x)

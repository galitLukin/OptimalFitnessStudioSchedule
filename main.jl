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
diff = 1000
ub = 1000

k = 1
# A is a vector of uncertainty matrices
Alist = []
newAs = []
firstA = firstUncertainty()
push!(newAs,firstA)
println("got A")
x = 0
while newAs != []
    for nextA in newAs
        push!(Alist,nextA)
    end
    x, ub = getSchedule(Alist)
    println("Got schedule, UB: $ub")
    if isnan(ub)
        break
    else
        newAs = buildUncertainties(ub,x)
        #println("Got wc, LB: $lb")
        #push!(Alist,nextA)
        #global diff = ub - lb
        #println("Diff is $diff")
    end
end
visualizeSchedule(x)

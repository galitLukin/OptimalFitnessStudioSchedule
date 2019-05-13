using DataFrames, MLDataUtils

include("formulation.jl")
include("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
L = 10
U = 55

# A is a vector of uncertainty matrices
allAs = []
newAs = []
firstA = firstUncertainty()
push!(newAs,firstA)
x = 0
ub = 0
vals = []
while newAs != []
    for nextA in newAs
        push!(allAs,nextA)
    end
    x, ub = getSchedule(allAs)
    push!(vals,ub)
    if isnan(ub)
        break
    else
        newAs = buildUncertainties(ub,x)
        s1 = size(newAs,1)
    end
end
visualizeSchedule(x)
println(iterations)
println(vals)
printDecisions(allAs[2])

using DataFrames, MLDataUtils

include("formulation.jl")
include("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
L = 15
U = 55

# A is a vector of uncertainty matrices
allAs = []
newAs = []
firstA = firstUncertainty()
push!(newAs,firstA)
println("got A")
x = 0
ub = 0
iterations = 0
vals = []
while newAs != []
    for nextA in newAs
        push!(allAs,nextA)
        s = size(allAs,1)
        println("length of allAs: $s")
    end
    x, ub = getSchedule(allAs)
    push!(vals,ub)
    println("Got schedule, UB: $ub")
    if isnan(ub)
        break
    else
        newAs = buildUncertainties(ub,x)
        s1 = size(newAs,1)
    end
    iterations = iterations + 1
end
visualizeSchedule(x)
println(iterations)
println(vals)

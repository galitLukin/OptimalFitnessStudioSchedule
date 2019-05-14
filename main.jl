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
alphas = [0:0.5:6;]
weeklyDemand, numClasses, numTeacher = [],[],[]
for alpha in alphas
    println(alpha)
    # A is a vector of uncertainty matrices
    allAs = []
    newAs = []
    firstA = firstUncertainty()
    push!(newAs,firstA)
    x = 0
    z = 0
    ub = 0
    vals = []
    while newAs != []
        for nextA in newAs
            push!(allAs,nextA)
        end
        x, z, ub = getSchedule(allAs,alpha)
        push!(vals,ub)
        if isnan(ub)
            break
        else
            newAs = buildUncertainties(ub, x, z, alpha)
            s1 = size(newAs,1)
        end
    end
    visualizeSchedule(x, alpha)
    println(vals)
    printDecisions(allAs[2],x)
end
println(weeklyDemand)
println(numClasses)
println(numTeacher)

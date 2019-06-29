using DataFrames, MLDataUtils

include("formulation.jl")
include("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
L = 7
U = 55
alphas = [0:4:12;]
betas = [0:5:20;]
weeklyDemandmin, weeklyDemandmax, numClasses, numTeacher = [],[],[], []
for alpha in alphas
    println(alpha)
    for beta in betas
        minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
        x, z, ub = getSchedule(minVals, maxVals, minWeekly, dailyMin, alpha,beta)
        visualizeSchedule(x, alpha, beta)
        printDecisions(minVals,maxVals,x)
    end
end
println(alphas)
println(betas)
println(weeklyDemandmin)
println(weeklyDemandmax)
println(numClasses)
println(numTeacher)

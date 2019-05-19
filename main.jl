using DataFrames, MLDataUtils

include("formulation.jl")
include("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
L = 9
U = 55
alphas = [0:6;]
betas = [0:2:10;]
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

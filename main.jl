using DataFrames, MLDataUtils
using Suppressor
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
allSubAsLower = []
allSubAsUpper = []
newAs = []
newSubAsLower = []
newSubAsUpper = []
firstA = firstUncertainty()
push!(newAs,firstA)
initiateSubAs(allSubAsLower, firstA)
initiateSubAs(allSubAsUpper, firstA)
for d in 1:D
    for t in 1:T
        for c in 1:C
            for i in 1:I
                push!(newSubAsLower,firstA[d,t,c,i])
                push!(newSubAsUpper,firstA[d,t,c,i])
            end
        end
    end
end
println("got A")
x = 0
ub = 0
iterations = 0
while newAs != [] || lowerIsEmpty == false || upperIsEmpty == false
    for nextA in newAs
        push!(allAs,nextA)
        s = size(allAs,1)
        println("length of allAs: $s")
    end
    x, ub = getSchedule(allAs, allSubAsLower, allSubAsUpper)
    println("Got schedule, UB: $ub")
    if isnan(ub)
        break
    else
        newAs, newSubAsLower, newSubAsUpper = buildUncertainties(ub,x)
        s1 = size(newAs,1)
        s2 = size(newSubAsLower,1)
        s3 = size(newSubAsUpper,1)
        println("lower violated")
        lowerIsEmpty = isSubEmpty(newSubAsLower)
        println("upper violated")
        upperIsEmpty = isSubEmpty(newSubAsUpper)
        println("size of As: $s1, $s2-isEmpty: $lowerIsEmpty, $s3-isEmpty: $upperIsEmpty")
        println("poplating lower")
        populateSubAs(allSubAsLower, newSubAsLower)
        println("poplating upper")
        populateSubAs(allSubAsUpper, newSubAsUpper)
    end
    iterations = iterations + 1
end
visualizeSchedule(x)
println(iterations)

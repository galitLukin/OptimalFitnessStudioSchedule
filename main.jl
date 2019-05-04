using DataFrames, MLDataUtils

include("formulation.jl")
include("uncertainty.jl")
include("utils.jl")

D = 7
T = 28
C = 8
I = 18
L = 1
U = 50

eps = 0
diff = 1000
ub = 1000

k = 1
# A is a vector of uncertainty matrices
A = []
firstA = firstUncertainty()
push!(A,firstA)
println("got A")
x = 0
while diff > eps
    x, ub = getSchedule(A)
    println("Got schedule, UB: $ub")
    nextA, lb = worstCase(x)
    # for d in 1:D
    #     for t in 1:T
    #         for c in 1:C
    #             for i in 1:I
    #                 if nextA[d,t,c,i] > 5
    #                     println(nextA[d,t,c,i])
    #                 end
    #             end
    #         end
    #     end
    # end
    println("Got wc, LB: $lb")
    push!(A,nextA)
    global diff = ub - lb
    println("Diff is $diff")
end
visualizeSchedule(x)

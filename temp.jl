using JuMP, JuMPeR, Gurobi

include("constraints.jl")

D = 7
T = 28
C = 8
I = 18
L = 5
U = 50

function staticUncertainty(model, A)
    u = readtable("Data/output/staticU.csv", header=true, makefactors=true)
    M = 500
    minVals = ones(Int64, D,T,C,I) * M
    maxVals = zeros(Int64, D,T,C,I)
    for k in 1:size(u, 1)
        d = Int8(floor(u[k,:D]))
        t = Int8(floor(u[k,:T]))
        c = Int8(floor(u[k,:C]))
        i = Int8(floor(u[k,:I]))
        mi = Int64(floor(u[k,:MinVal]))
        ma = Int64(floor(u[k,:MaxVal]))

        if mi < minVals[d,t,c,i]
            minVals[d,t,c,i] = mi
        end
        if ma > maxVals[d,t,c,i]
            maxVals[d,t,c,i] = ma
        end
    end

    maxDayVals = zeros(Int64, D)
    for d in 1:D
        slots = zeros(Int64, 28)
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    if maxVals[d,t,c,i] > slots[t]
                        slots[t] = maxVals[d,t,c,i]
                    end
                end
            end
        end
        maxDayVals[d] = sum(slots)
    end

    for d in 1:D
        @constraint(model, sum(A[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) <= maxDayVals[d] - 500)
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    @constraint(model, A[d,t,c,i] >= minVals[d,t,c,i])
                    @constraint(model, A[d,t,c,i] <= maxVals[d,t,c,i])
                end
            end
        end
    end
end



model = RobustModel(solver=GurobiSolver(OutputFlag=0))
# if scheduled or not
@variable(model, x[1:D,1:T,1:C,1:I], Bin)
@variable(model, y)
@uncertain(model, A[1:D,1:T,1:C,1:I])

@objective(model, Max, y)
# this will be robust - comes from objective function
@constraint(model, y <= sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))

# How many class types per day/week
classTypeOccurence(model, x)

# Instructor schedule constraints
instructorSchedule(model, x)

# Instructor special schedule constraints
instructorSpecialSchedule(model, x)

# Instructor class type constraints
instuctorClassType(model, x)

# studio feasibility constraints
studio(model, x)

# this will be robust
# max/min in each class
for d in 1:D
    for t in 1:T
        for c in 1:C
            for i in 1:I
                @constraint(model, L*x[d,t,c,i] <= A[d,t,c,i])
                @constraint(model, A[d,t,c,i]*x[d,t,c,i] <= U)
            end
        end
    end
end

solve(model)
xVals = getvalue(x)
objective = getobjectivevalue(model)
println(objective)

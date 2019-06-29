using JuMP, Gurobi

include("constraints.jl")

function getSchedule(minA, maxA, minWeekly, dailyMin, alpha, beta)
    model = Model(solver=GurobiSolver(OutputFlag=0))
    # if scheduled or not
    @variable(model, x[1:D,1:T,1:C,1:I], Bin)
    @variable(model, z[1:I,1:C], Bin)
    @variable(model, y)

    @objective(model, Max, y)
    # this will be robust - comes from objective function
    @constraint(model, y <= sum(minA[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I) + alpha * sum(z[i,c] for i=1:I, c=:1:C) - beta * sum(x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))

    # How many class types per day/week
    classTypeOccurence(model, x)

    # Instructor schedule constraints
    instructorSchedule(model, x)

    # Instructor special schedule constraints
    instructorSpecialSchedule(model, x)

    # Instructor class type constraints
    instuctorClassType(model, x)

    # Instructor class type constraints
    instuctorFairness(model, x, z)

    # studio feasibility constraints
    studio(model, x)

    # max/min in each class
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    @constraint(model, L*x[d,t,c,i] <= minA[d,t,c,i])
                    @constraint(model, maxA[d,t,c,i]*x[d,t,c,i] <= U)
                end
            end
        end
    end
    # for d in 1:D
    #     @constraint(model, sum(minA[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) >= dailyMin[d])
    # end

    #@constraint(model, minWeekly <= sum(minA[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))

    solve(model)
    xVals = getvalue(x)
    zVals = getvalue(z)
    objective = getobjectivevalue(model)
    return xVals, zVals, objective
end

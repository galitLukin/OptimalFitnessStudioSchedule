using DataFrames, JuMP

function firstUncertainty()
    lastWeekSchedule = readtable("Data/output/attendanceLastWeekIndex.csv", header=true, makefactors=true)
    a = zeros(Int8, D,T,C,I)
    for k in 1:size(lastWeekSchedule, 1)
        d = lastWeekSchedule[k, :WeekDay]
        t = lastWeekSchedule[k, :StartTime]
        c = lastWeekSchedule[k, :Description]
        i = lastWeekSchedule[k, :Staff]
        a[d,t,c,i] = lastWeekSchedule[k, :Arrivals]
    end
    return a
end

function buildUncertainties(obj,x)
    minVals, maxVals = calcRanges()
    newAs = []
    feasible, A = wcArrivals(obj, x, minVals, maxVals)
    if ~feasible
        push!(newAs,A)
    end
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    mi, ma = minVals[d,t,c,i], maxVals[d,t,c,i]
                    feasible, A = wcLB(d,t,c,i,mi,ma)
                    if ~feasible
                        push!(newAs,A)
                    end
                end
            end
        end
    end
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    mi, ma = minVals[d,t,c,i], maxVals[d,t,c,i]
                    feasible, A = wcUB(d,t,c,i,mi,ma)
                    if ~feasible
                        push!(newAs,A)
                    end
                end
            end
        end
    end
    return newAs
end

function wcLB(d,t,c,i,mi,ma)
    wc = Model(solver=GurobiSolver(OutputFlag=0))
    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)
    @objective(wc, Max, L*x[d,t,c,i] - A[d,t,c,i])
    @constraint(wc, A[d,t,c,i] >= mi)
    @constraint(wc, A[d,t,c,i] <= ma)
    solve(wc)
    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVals
    end
    return true, aVals
end

function wcUB(d,t,c,i,mi,ma)
    wc = Model(solver=GurobiSolver(OutputFlag=0))
    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)
    @objective(wc, Max, A[d,t,c,i]*x[d,t,c,i] - U)
    @constraint(wc, A[d,t,c,i] >= mi)
    @constraint(wc, A[d,t,c,i] <= ma)
    solve(wc)
    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVals
    end
    return true, aVals
end

function wcArrivals(obj, x, minVals, maxVals)
    # solve worst case min problem - formulate WC
    wc = Model(solver=GurobiSolver(OutputFlag=0))

    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)

    @objective(wc, Max, obj - sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    @constraint(wc, A[d,t,c,i] >= minVals[d,t,c,i])
                    @constraint(wc, A[d,t,c,i] <= maxVals[d,t,c,i])
                end
            end
        end
    end

    solve(wc)
    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVals
    end
    return true, aVals
end

function calcRanges()
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
    end
    return minVals, maxVals
end

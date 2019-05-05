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
    minVals, maxVals = calcRanges2()
    As = []
    AsLower = []
    AsUpper = []
    i = 1
    feasible, A, objective = wcArrivals(obj, x, minVals, maxVals)
    if ~feasible && objective >= 1
        push!(As,A)
    end
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    mi, ma = minVals[d,t,c,i], maxVals[d,t,c,i]
                    feasible, A = wcLB(x[d,t,c,i],mi,ma)
                    if ~feasible
                        push!(AsLower,A)
                    else
                        push!(AsLower,-1)
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
                    feasible, A = wcUB(x[d,t,c,i],mi,ma)
                    if ~feasible
                        push!(AsUpper,A)
                    else
                        push!(AsUpper,-1)
                    end
                end
            end
        end
    end
    return As, AsLower, AsUpper
end

function wcLB(x,mi,ma)
    wc = Model(solver=GurobiSolver(OutputFlag=0))
    @variable(wc, A>=0)
    @objective(wc, Max, L*x - A)
    @constraint(wc, A >= mi)
    @constraint(wc, A <= ma)
    solve(wc)
    aVal = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVal
    end
    return true, aVal
end

function wcUB(x,mi,ma)
    wc = Model(solver=GurobiSolver(OutputFlag=0))
    @variable(wc, A>=0)
    @objective(wc, Max, A*x - U)
    @constraint(wc, A >= mi)
    @constraint(wc, A <= ma)
    solve(wc)
    aVal = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVal
    end
    return true, aVal
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
    for d in 1:D
        @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) >= 40)
        @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) >= 250)
    end
    solve(wc)
    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVals, objective
    end
    return true, [], objective
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

function calcRanges2()
    uMin = readtable("Data/output/staticUMin.csv", header=true, makefactors=true)
    uMax = readtable("Data/output/staticUMin.csv", header=true, makefactors=true)
    minVals = zeros(Int64, D,T,C,I)
    maxVals = zeros(Int64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    row = (d-1)*224 + (t-1)*8 + c
                    minVals[d,t,c,i] = uMin[row,i]
                    maxVals[d,t,c,i] = uMax[row,i]
                end
            end
        end
    end
    return minVals, maxVals
end

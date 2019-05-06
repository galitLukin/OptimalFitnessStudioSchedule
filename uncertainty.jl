using DataFrames, JuMP

function firstUncertaintyOrig()
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

function firstUncertainty()
    minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
    a = zeros(Int64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    mi, ma = minVals[d,t,c,i], maxVals[d,t,c,i]
                    a[d,t,c,i] = Int64(floor((mi + ma)/2))
                    # if ma > 0
                    #     a[d,t,c,i] = 55#Int64(floor((mi + ma)/2))
                    # end
                end
            end
        end
    end
    for d in 1:D
        if sum(a[d,t,c,i] for t=1:T, c=1:C, i=1:I) < dailyMin[d]
             for t in 1:T
                 for c in 1:C
                     for i in 1:I
                         a[d,t,c,i] = maxVals[d,t,c,i]
                     end
                 end
             end
        end
    end
    if sum(a[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I) < minWeekly
        diff = minWeekly - sum(a[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I)
        while diff > 0
            d = rand(1:D)
            t = rand(1:T)
            c = rand(1:C)
            i = rand(1:I)
            add = maxVals[d,t,c,i] - a[d,t,c,i]
            a[d,t,c,i] = a[d,t,c,i] + add
            diff = diff - add
        end
    end
    for k in 1:2000
        d = rand(1:D)
        t = rand(1:T)
        c = rand(1:C)
        i = rand(1:I)
        if a[d,t,c,i] > 0
            a[d,t,c,i] = 55
        end
    end
    return a
end

function buildUncertainties(obj,x)
    minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax = calcRanges()
    As = []
    AsLower = []
    AsUpper = []
    i = 1
    feasible, A, objective = wcArrivals(obj, x, minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax)
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

function wcArrivals(obj, x, minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax)
    # solve worst case min problem - formulate WC
    wc = Model(solver=GurobiSolver(OutputFlag=0))

    @variable(wc, A[1:D,1:T,1:C,1:I]>=0)

    @objective(wc, Max, obj - sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I))
    # for d in 1:D
    #     for t in 1:T
    #         for c in 1:C
    #             for i in 1:I
    #                 @constraint(wc, A[d,t,c,i] >= minVals[d,t,c,i])
    #                 @constraint(wc, A[d,t,c,i] <= maxVals[d,t,c,i])
    #             end
    #         end
    #     end
    # end
    for d in 1:D
        @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for t=1:T, c=1:C, i=1:I) >= dailyMin[d])
    end
    @constraint(wc, sum(A[d,t,c,i]*x[d,t,c,i] for d=1:D, t=1:T, c=1:C, i=1:I) >= minWeekly)
    solve(wc)
    aVals = getvalue(A)
    objective = getobjectivevalue(wc)
    if objective > 0
        return false, aVals, objective
    end
    return true, [], objective
end

function calcRanges()
    uMin = readtable("Data/output/staticUMin.csv", header=true, makefactors=true)
    uMax = readtable("Data/output/staticUMin.csv", header=true, makefactors=true)
    minVals = zeros(Int64, D,T,C,I)
    maxVals = zeros(Int64, D,T,C,I)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    row = (d-1)*T*C + (t-1)*C + c
                    minVals[d,t,c,i] = uMin[row,i]
                    maxVals[d,t,c,i] = uMax[row,i]
                end
            end
        end
    end
    uDaily = readtable("Data/output/staticUDaily.csv", header=true, makefactors=true)
    minWeekly, maxWeekly = uDaily[1,:MinVal], uDaily[1,:MaxVal]
    dailyMin = []
    dailyMax = []
    for i=2:8
         push!(dailyMin, uDaily[i,:MinVal])
         push!(dailyMax, uDaily[i,:MaxVal])
    end
    return minVals, maxVals, minWeekly, maxWeekly, dailyMin, dailyMax
end

using DataFrames

function visualizeSchedule(x)
    classes = ["HOT 26", "HOT 26 FLOW", "SILENT HOT 26", "HOT 26+", "INFERNO HOT PILATES", "INFERNO HOT PILATES LEVEL II", "HOT HATHA FUSION", "HOT HATHA SCULPT"]
    instructors = ["ANCIVAL, SOPHIE", "BOU-NASSIF, JASMINE", "BOUJOULIAN, RACHELLE", "CATES, SHELLEY", "EVANGELISTI, MEREDITH", "HEIRTZLER, LESLIE", "JONES, JACLYN", "LAMBERT, LUCAS", "LANSING, LUCAS", "LOVERME, KYLA", "MCGRATH, SHARON", "MONROE, KYLAH", "PHAN, STEVEN", "PIGOTT, ELLEN", "SERRANO, JIMMY", "STERN, BRIAN", "VEERAPEN, KUMAR", "WOODS, TESS"]

    schedule = DataFrame( Time = Float64[], Monday = String[] , Tuesday = String[], Wednesday = String[], Thursday = String[], Friday = String[], Saturday = String[], Sunday = String[])
    for t in 1:T
        realTime = 6 + (t-1)*0.5
        push!(schedule,[realTime,"","","","","","",""])
    end
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    if x[d,t,c,i] == 1
                        #println("$d,$t,$c,$i")
                        chosenClass = classes[c]
                        chosenInstructor = instructors[i]
                        schedule[t,d+1] = "$chosenClass-$chosenInstructor"
                    end
                end
            end
        end
    end
    writetable("Data/output/schedule.csv",schedule)
end

function populateSubAs(allSubAs,newSubAs)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    ind = (d-1)*4032 + (t-1)*144 + (c-1)*18 + i
                    if newSubAs[ind] >= 0
                        println(ind)
                        println(newSubAs[ind])
                        push!(allSubAs[ind],newSubAs[ind])
                    end
                end
            end
        end
    end
end

function initiateSubAs(allSubAs, firstA)
    for d in 1:D
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    push!(allSubAs,[firstA[d,t,c,i]])
                end
            end
        end
    end
end

function isSubEmpty(subAs)
    k = 0
    violated = []
    for val in subAs
        if val != -1
            push!(violated, k)
        end
        k = k + 1
    end
    for v in violated
        println("violated constraints: $v")
    end
    if size(violated,1) >= 1
        return false
    end
    return true
end

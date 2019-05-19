using DataFrames

function visualizeSchedule(x,alpha,beta)
    classes = ["HOT 26", "HOT 26 FLOW", "SILENT HOT 26", "HOT 26+", "INFERNO HOT PILATES", "INFERNO HOT PILATES LEVEL II", "HOT HATHA FUSION", "HOT HATHA SCULPT"]
    instructors = ["ANCIVAL, SOPHIE", "BOU-NASSIF, JASMINE", "BOUJOULIAN, RACHELLE", "CATES, SHELLEY", "EVANGELISTI, MEREDITH", "HEIRTZLER, LESLIE", "JONES, JACLYN", "LAMBERT, LUCAS", "LANSING, LUCAS", "LOVERME, KYLA", "MCGRATH, SHARON", "MONROE, KYLAH", "PHAN, STEVEN", "PIGOTT, ELLEN", "SERRANO, JIMMY", "STERN, BRIAN", "VEERAPEN, KUMAR", "WOODS, TESS"]
    instructorsPrivate = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R"]
    classesShort =  ["HOT 26", "HOT 26 FLOW", "SILENT HOT 26", "HOT 26+", "IHP", "IHP II", "HHF", "HHS"]

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
                        chosenClass = classesShort[c]
                        chosenInstructor = instructorsPrivate[i]
                        schedule[t,d+1] = "$chosenClass Instructor $chosenInstructor"
                    end
                end
            end
        end
    end
    writetable("Data/output/schedule_$alpha-$beta.csv",schedule)
end


function printDecisions(aMin,aMax,x)
    weekDemandmin = 0
    weekDemandmax = 0
    classes = 0
    teachers = zeros(18)
    for d in 1:D
        demandmin = 0
        demandmax = 0
        for t in 1:T
            for c in 1:C
                for i in 1:I
                    if x[d,t,c,i] == 1
                        teachers[i] = 1
                        bmin = aMin[d,t,c,i]
                        bmax = aMax[d,t,c,i]
                        demandmin = demandmin + bmin
                        demandmax = demandmax + bmax
                        classes = classes + 1
                        println("Day:$d,Time:$t,Class:$c,Instructor:$i,: $bmin, $bmax")
                    end
                end
            end
        end
        println("Day: $d: $demandmin, $demandmax")
        weekDemandmin = weekDemandmin + demandmin
        weekDemandmax = weekDemandmax + demandmax
    end
    t = sum(teachers)
    push!(weeklyDemandmin, weekDemandmin)
    push!(weeklyDemandmax, weekDemandmax)
    push!(numClasses, classes)
    push!(numTeacher, t)
    println("Weekly Demand: $weekDemandmin, $weekDemandmax")
    println("Number of Classes: $classes")
    println("Number of Teachers: $t")
end

#This script is made for Kaggle springleaf competition"
##j.z. won top 25% w/ this script

date = Sys.time()

#define working directory
setwd('D:kaggle/springleaf/')

#load packages
library(readr)
library(xgboost)



set.seed(123)

###read data
 #importance = read_csv("importance_0035_1500.csv")
 #impfeature <- importance$Feature[1:1450] ##sum gain = 0.99 turn on after save importance matrix from previous run
 
 train = read_csv("input/train.csv")
 test= read_csv("input/test.csv")
 
 trainY  = train$target
 testID  = test$ID
 test    = test[,-1] #delete ID
 train   = train[,-1]  #delete ID 

##find constant variables and delete

 first delete the ones with only one value
 col_const = sapply(train, function(x) length(unique(x)))
 train    = train[,!names(train) %in% names(col_const[col_const==1])]
 test    =  test[,!names(test) %in% names(col_const[col_const==1])]
 

 ### second check the ones with two unique values results show that only the ones with same unique values as target is valid
 col_const2=sapply(train[,names(train) %in% names(col_const[col_const==2])],function(x) unique(x))
 col_const2 = as.data.frame(col_const2)
 col_const22 = sapply(col_const2,function(x) identical(x,as.factor(unique(trainY))))
 train       = train[,!names(train) %in% names(col_const2[col_const22=="FALSE"])]
 test        = test[, !names( test) %in% names(col_const2[col_const22=="FALSE"])]
 
 ###find character variables & save it, manually check them and store brief info
 ### in file characterVar too, comment it out after 1st run
  trainChar   =  names(train)[sapply(train, function(x) class(x)=="character")]
 #dput(trainChar,"characterVar")
  
 ###so dates variable leftover : VAR_0075 (earliest),VAR_0204 (latest), VAR_0217 
 ##looks like VAR_0075 starts date and VAR_0204 last record date from 01/29/14-02/01/14(??)
 ## change to format year-month-day
  test$VAR_0217  <- as.Date(substr(test$VAR_0217,1,7),"%d%b%y") #398 diff days
  test$VAR_0204  <- as.Date(substr(test$VAR_0204,1,7),"%d%b%y")
  test$VAR_0075  <- as.Date(substr(test$VAR_0075,1,7),"%d%b%y")
  train$VAR_0217 <- as.Date(substr(train$VAR_0217,1,7),"%d%b%y") #398 diff days
  train$VAR_0204 <- as.Date(substr(train$VAR_0204,1,7),"%d%b%y")
  train$VAR_0075 <- as.Date(substr(train$VAR_0075,1,7),"%d%b%y")
  ##get some time difference
   train$Year1  <- as.integer((train$VAR_0204-train$VAR_0075)/365)
   train$Year2  <- as.integer((train$VAR_0217-train$VAR_0075)/365) 
   test$Year1  <- as.integer((test$VAR_0204-test$VAR_0075)/365)
   test$Year2  <- as.integer((test$VAR_0217-test$VAR_0075)/365) 
   ##get starting year, month sepeartely
   train$VAR_0075Y <- as.integer(substr(train$VAR_0075,1,4))
   test$VAR_0075Y  <- as.integer(substr(test$VAR_0075,1,4)) 
   train$VAR_0075M <- as.integer(substr(train$VAR_0075,6,7))
   test$VAR_0075M  <- as.integer(substr(test$VAR_0075,6,7))
   train$VAR_0217Y <- as.integer(substr(train$VAR_0217,1,4))
   test$VAR_0217Y  <- as.integer(substr(test$VAR_0217,1,4)) 
   train$VAR_0217M <- as.integer(substr(train$VAR_0217,6,7))
   test$VAR_0217M  <- as.integer(substr(test$VAR_0217,6,7))


 
 ##check whether VAR_0237 and VAR_0274 the same state
   train$stateID  <- 0
   test$stateID   <- 0
   train$stateID[train$VAR_0237 == train$VAR_0274] <- 1
   test$stateID[test$VAR_0237 == test$VAR_0274] <- 1

 #feature.names <- names(train)[ -which( names(train) %in% c("VAR_0073","VAR_0156",
                    "VAR_0157","VAR_0158","VAR_0159","VAR_0166","VAR_0167","VAR_0168",
                 "VAR_0169","VAR_0176","VAR_0177","VAR_0178","VAR_0179","VAR_0075","VAR_0204",
                  "VAR_0217","VAR_0466","target"))]
 
#feature.names <- impfeature ##can be used after run one model and get the importance matrix
### following Ben Hamner in Sprinleaf Marketing Response example scripts
cat("assuming text variables are categorical & replacing them with numeric ids\n")
 for (trainX in feature.names) {
      if (class(train[[trainX]]) =="character") {
       levels = unique(c(train[[trainX]],test[[trainX]]))
     train[[trainX]] <- as.integer(factor(train[[trainX]],levels = levels))
     test[[trainX]]  <- as.integer(factor(test[[trainX]],levels = levels))
  }
}

 cat("replacing missing values with -9991\n")
 train[,feature.names][is.na(train[,feature.names])] <- -9991
 test[,feature.names][is.na(test[,feature.names])]   <- -9991  
 
  cat("training a XGBoost classifier\n")
  
 ###using watchlist to find best rounds saving 10% training for eval
   
  gc()
  hold <- sample(1:nrow(train), 14400)
 
  xgtrain <- xgb.DMatrix(as.matrix(train[-hold,feature.names]),label = train$target[-hold])#, missing = -9991)

  xgval   <- xgb.DMatrix(as.matrix(train[hold,feature.names]),label = train$target[hold])#, missing = -9991)


  watchlist <- list('val'=xgval)


   clf = xgb.train(data             = xgtrain,
                  eta             = 0.035,  # 0.06,  0.009  three optimal from xgb.cv
               nrounds            = 4000,
               objective          = "binary:logistic",
               max_depth          =  5, # 6 two values from xgb.cv
               early.stop.round   = 20,
               eval_metric        = "auc",
               eval.metric        = "logloss",
               colsample_bytree   = 0.8,
               watchlist          = watchlist,
               print.every.n      = 5,
                  subsample       = 0.7)

cat ("\nwatchlist best score", clf$bestScore)

        
cat("making predictions")
submission = data.frame(ID=testID)
submission$target = NA
 for (rows in split(1:nrow(test),ceiling((1:nrow(test))/10000))) {
  submission[rows,"target"] = predict(clf,data.matrix(test[rows,feature.names]))
}

write_csv(submission,paste("valauc-", clf$bestScore,"submission.csv"))
  rm("xgval")
  rm("xgtrain")   
  rm("hold")
 ##get the importance matrix
  importance_matrix<- xgb.importance(feature.names,model = clf)
  write_csv(importance_matrix,paste("valauc-",clf$bestScore,"importance.csv"))
  xgb.plot.importance(importance_matrix[1:10,])
 
   rm("submission")
   rm("clf")


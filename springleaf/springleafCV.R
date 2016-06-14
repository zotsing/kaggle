#This script is made for Kaggle springleaf competition"
## used xgb.cv to tune parameter

date = Sys.time()

#define working directory
setwd('D:kaggle/springleaf/')

#load packages
library(readr)
library(xgboost)



set.seed(123)

###read data
 train = read_csv("input/train.csv")
 test= read_csv("input/test.csv")
 train <- train[sample(nrow(train), 10000),]
 trainY  = train$target
 testID  = test$ID
 test    = test[,-1] #delete ID
 train   = train[,-1]  #delete ID 

 

##find constant variables and delete

  ##first delete the ones with only one value
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
 ## trainChar   =  names(train)[sapply(train, function(x) class(x)=="character")]
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

 feature.names <- names(train)[ -which( names(train) %in% c("VAR_0073","VAR_0156",
                   "VAR_0157","VAR_0158","VAR_0159","VAR_0166","VAR_0167","VAR_0168",
                 "VAR_0169","VAR_0176","VAR_0177","VAR_0178","VAR_0179","VAR_0075","VAR_0204",
                  "VAR_0217","VAR_0466","target"))]
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

 gc()

##product input data
  
  train <- train[sample(nrow(train), 10000),]

  #dtrain <- xgb.DMatrix(as.matrix(train[,feature.names]),label  = train$target) # can turned on if having a saved matrix
  #xgb.DMatrix.save(dtrain,"xgbcv-1015.DMatrix.data")
  ##use CV to determine parameters
 
testauc = 0.5

for (depth in 4:10) {
  for (etaa in seq(0.001,0.3,0.005)) { 
     for (fold in 4:10){
          clf1 =  xgb.cv(data         = dtrain,
                         eta        = etaa,
                         nfold      = fold,
                       nrounds      = 500,
                       objective    = "binary:logistic",
                       max_depth    = depth,
                       verbose      = 0,
                    early.stop.round = 5,
                   eval_metric  = "auc")
             if (testauc < max(clf1$test.auc.mean-clf1$test.auc.std)){
                  testauc <- max(clf1$test.auc.mean-clf1$test.auc.std)
                  print(c("Better record",which((clf1$test.auc.mean-clf1$test.auc.std)==testauc),depth, etaa, fold, testauc))}

            }
   }
}

            

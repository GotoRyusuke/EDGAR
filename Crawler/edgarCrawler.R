library(edgar)
library(qdapRegex)
library(stringr)
library(XML)
library(tm)
library(writexl)
library(readxl)

export2excel <- function(df, form.type, filename){
  exl = df[,1:4]
  names(exl) = c('CIK','co_name','f_type','f_date')
  
  f_name = c()
  for (i in 1:nrow(df)) {
    main.file = paste('F:/EDGAR/Edgar filings_full text/Form',form.type)
    child.file = df$cik[i]
    parent.address = paste(main.file,child.file, sep = '/')
    acc.num = strsplit(strsplit(df$edgar.link[i],'[.]')[[1]][1], '/')[[1]][4]
    
    temp.name = paste(acc.num,
                       '.txt',
                       sep = '')
    
    full.name = paste(df$cik[i],
                       df$form.type[i],
                       df$date.filed[i],
                       temp.name,
                       sep = '_')
    
    local.address = paste(parent.address,'/',full.name,sep = '')
    f_name[i] = local.address
  }
  exl$f_name = f_name
  
  write_xlsx(exl,filename)
  # return(exl)
}

## preparation for crawling
setwd("F:/EDGAR")
myid <- 'GOTO Ryusuke niccolologne@gmail.com'

# get master index
getMasterIndex(2022,myid)
load("F:/EDGAR/Master Indexes/2022master.Rda")
edgarR4 <- year.master

## 8-K forms
R4.8K <- edgarR4[edgarR4$form.type=='8-K',]
R4.8K.Q3 <- R4.8K[R4.8K$quarter == 3,]

export2excel(R4.8K.Q3,'8-K', 'F:/EDGAR/2022Q2_8-K.xlsx')


## 10-K forms
R4.10K <- edgarR4[edgarR4$form.type == '10-K',]
R4.10K.Q3 <- R4.10K[R4.10K$quarter == 3,]

## 10-Q forms
R4.10Q <- edgarR4[edgarR4$form.type == '10-Q',]
R4.10Q.Q2 <- R4.10Q[R4.10Q$quarter == 2,]
code.list.Q2 <- unique(R4.10Q.Q2$cik)

R4.10Q.Q3 <- R4.10Q[R4.10Q$quarter == 3,]
code.list.Q3 <- unique(R4.10Q.Q3$cik)

R4.10Q.Q1 <- R4.10Q[R4.10Q$quarter == 1,]
code.list.Q1 <- unique(R4.10Q.Q1$cik)

## get 10-Q forms
ciks.10Q <- unique(read_excel('F:/EDGAR/2022Q2_10-Q_sup2.xlsx')$CIK)
get.R4Q3.10Q <- getFilings(ciks.10Q,
                          '10-Q',
                          2022,
                          3,
                          useragent = myid)
## get 10-K forms
ciks.10K <- unique(read_excel('F:/EDGAR/2022Q2_10-K_sup2.xlsx')$CIK)
get.R4Q3.10K <- getFilings(ciks.10K,
                           '10-K',
                           2022,
                           3,
                           useragent = myid)

## get 8-K forms
ciks.8k <- unique(read_excel('F:/EDGAR/2022Q2_8-K_sup2.xlsx')$CIK)

get.R4Q3.8K <- getFilings(ciks.8k,
                          '8-K',
                           2022,
                           3,
                           useragent = myid)

# export to Excel
export2excel(R4.10K.Q3,'10-K','F:/EDGAR/2022Q2_10-K.xlsx')
export2excel(R4.8K.Q3,'8-K','F:/EDGAR/2022Q2_8-K.xlsx')
export2excel(R4.10Q.Q3,'10-Q','F:/EDGAR/2022Q2_10-Q.xlsx')

# test get8kitem
test <- get8KItems(1000045, 2022, myid)


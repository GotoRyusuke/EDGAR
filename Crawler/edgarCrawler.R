library(edgar)
library(qdapRegex)
library(stringr)
library(XML)
library(tm)
library(writexl)

export2excel <- function(df, form.type, filename){
  exl = df[,1:4]
  names(exl) = c('CIK','CompanyName','FormType','FilingDate')
  
  FileName = c()
  for (i in 1:nrow(df)) {
    main.file = paste('F:/EDGAR/Edgar filings_full text/Form ',form.type)
    child.file = df$cik[i]
    parent.address = paste(main.file,child.file, sep = '/')
    
    temp.name = paste(df$accession.number[i],
                       '.txt',
                       sep = '')
    
    full.name = paste(df$cik[i],
                       df$form.type[i],
                       df$date.filed[i],
                       temp.name,
                       sep = '_')
    
    local.address = paste(parent.address,'/',full.name,sep = '')
    FileName[i] = local.address
  }
  exl$FileName = FileName
  
  write_xlsx(exl,filename)
}

## preparation for crawling
setwd("F:/EDGAR")
myid <- 'GOTO Ryusuke niccolologne@gmail.com'

# get master index
getMasterIndex(2022,myid)
load("F:/EDGAR/Master Indexes/2022master.Rda")
edgarR4 <- year.master

R4.Q2 <- edgarR4[edgarR4$quarter == 2,]
## 8-K forms
R4.8K <- edgarR4[edgarR4$form.type=='8-K',]
R4.8K.Q2 <- R4.8K[R4.8K$quarter == 2,]

## 10-K forms
R4.10K <- edgarR4[edgarR4$form.type == '10-K',]
R4.10K.Q2 <- R4.10K[R4.10K$quarter == 2,]

## 10-Q forms
R4.10Q <- edgarR4[edgarR4$form.type == '10-Q',]
R4.10Q.Q2 <- R4.10Q[R4.10Q$quarter == 2,]
code.list.Q2 <- unique(R4.10Q.Q2$cik)

R4.10Q.Q3 <- R4.10Q[R4.10Q$quarter == 3,]
code.list.Q3 <- unique(R4.10Q.Q3$cik)

## get 10-Q forms
get.R4Q3.10Q <- getFilings('ALL',
                      '10-Q',
                      2022,
                      3,
                      useragent = myid)
## get 10-K forms
get.R4Q2.10K <- getFilings('ALL',
                           '10-K',
                           2022,
                           2,
                           useragent = myid)

# export to Excel
export2excel(get.R4Q2.10K,'10-K','F:/EDGAR/2022Q2_10-K.xlsx')
export2excel(get.R4Q2.8K,'8-K','F:/EDGAR/2022Q2_8-K.xlsx')
export2excel(get.R4Q2.10Q,'10-Q','F:/EDGAR/2022Q2_10-Q.xlsx')

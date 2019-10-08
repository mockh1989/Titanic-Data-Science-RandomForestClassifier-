#!/usr/bin/env python
# coding: utf-8

# In[1]:


# data analysis and wrangling
import pandas as pd
import numpy as np
import random as rnd

# visualization
import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')

# machine learning
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier


# In[2]:


train_df = pd.read_csv('train.csv')
test_df = pd.read_csv('test.csv')
combine = [train_df, test_df]


# In[3]:


print(train_df.columns.values)


# In[4]:


train_df.head()


# In[5]:


train_df.tail()


# ## Which features contain blank, null or empty values?
# 
# These will require correcting.
# 
# > Cabin > Age > Embarked features contain a number of null values in that order for the training dataset.
# > Cabin > Age are incomplete in case of test dataset.
# ## What are the data types for various features?
# 
# Helping us during converting goal.
# 
# > Seven features are integer or floats. Six in case of test dataset.
# > Five features are strings (object).

# In[6]:


train_df.info()
# print 用黎分隔 train 同 test 姐
print('_'*50)
test_df.info()


# In[7]:


train_df.describe()
# Review survived rate using `percentiles=[.61, .62]` knowing our problem description mentions 38% survival rate.
# Review Parch distribution using `percentiles=[.75, .8]`
# SibSp distribution `[.68, .69]`
# Age and Fare `[.1, .2, .3, .4, .5, .6, .7, .8, .9, .99]`


# In[8]:


train_df.describe(include=['O'])


# In[9]:


# check correlation between Pclass and Survived
train_df[['Pclass', 'Survived']].groupby(['Pclass'], as_index=False).mean().sort_values(by='Survived', ascending=False)


# 點解求Mean就 OK ? 因為Survived 既值是 1, 0 ，所以 mean 即係 Expected Value 。如果Survived 既值是 2,8 ，咁就唔可以用 mean 啦。

# In[10]:


# check correlation between Sex and Survived
train_df[['Sex', 'Survived']].groupby(['Sex'], as_index=False).mean().sort_values(by='Survived', ascending=False)


# In[11]:


# check correlation between Sibsp(兄弟姊妹＋老婆丈夫數量) and Survived
train_df[['SibSp', 'Survived']].groupby(['SibSp'], as_index=False).mean().sort_values(by='Survived', ascending=False)


# In[12]:


# check correlation between parch(父母小孩的數量) and Survived
train_df[['Parch', 'Survived']].groupby(['Parch'], as_index=False).mean().sort_values(by='Survived', ascending=False)


# ## 下面係用圖分析年齡同生存率既相關性

# In[13]:


#bins=20 --> dAge = Mix(Age)/ bins
g = sns.FacetGrid(train_df, col="Survived", margin_titles=True)
g.map(plt.hist, 'Age', bins=20)


# ## 下面係用圖分析船艙，年齡同生存率既相關性

# In[14]:


# grid = sns.FacetGrid(train_df, col='Pclass', hue='Survived')
grid = sns.FacetGrid(train_df, col='Survived', row='Pclass', size=2.2, aspect=1.6)
grid.map(plt.hist, 'Age', alpha=.5, bins=20)
grid.add_legend();


# ### Correlating numerical and ordinal features
# 
# We can combine multiple features for identifying correlations using a single plot. This can be done with numerical and categorical features which have numeric values.
# 
# **Observations.**
# 
# - Pclass=3 had most passengers, however most did not survive.Pclass3 擁有最多的乘客，但是大多數沒有倖存。 Confirms our classifying assumption #2.
# - Infant passengers in Pclass=2 and Pclass=3 mostly survived.Pclass2 和Pclass3 的嬰兒大部分倖存。 Further qualifies our classifying assumption #2.
# - Most passengers in Pclass=1 survived.在Pclass1 大多數乘客倖免於難。 Confirms our classifying assumption #3.
# - Pclass varies in terms of Age distribution of passengers. Pclass的年齡分佈方面有所不同。
# 
# **Decisions.**
# 
# - Consider Pclass for model training.使用Pclass進行模型訓練

# ## 下面係用圖分析船艙，港口，性別同生存率既相關性(以概率表示)

# In[15]:


# grid = sns.FacetGrid(train_df, col='Embarked'(登船港口))
grid = sns.FacetGrid(train_df, row='Embarked', size=2.2, aspect=1.6)
grid.map(sns.pointplot, 'Pclass', 'Survived', 'Sex', palette='deep')
grid.add_legend()


# ### Correlating categorical features
# 
# Now we can correlate categorical features with our solution goal.
# 
# **Observations.**
# 
# - Female passengers had much better survival rate than males. Confirms classifying (#1).女乘客有更好的生存率高於男性。
# - Exception in Embarked=C where males had higher survival rate. This could be a correlation between Pclass and Embarked and in turn Pclass and Survived, not necessarily direct correlation between Embarked and Survived.在港口C的話，男性存活率較高。 這可能是 Pclass與“港口”之間的關聯，也可能是Pclass與“生存率”之間的關聯，卻不一定是“港口”與“生存”之間的直接關聯。
# - Males had better survival rate in Pclass=3 when compared with Pclass=2 for C and Q ports.港口C的男性在所有Plcass生存率都高，以港口C的Pclass3男性生存率與 港口Q的 Pclass2 比較，港口C的生存率也比較高。 Completing (#2).
# - Ports of embarkation have varying survival rates for Pclass=3 and among male passengers.不同港口對Pclass3的男性客生存率影響各不相同。 Correlating (#1).
# 
# **Decisions.**
# 
# - Add Sex feature to model training.
# - Complete and add Embarked feature to model training.

# In[16]:


# grid = sns.FacetGrid(train_df, col='Embarked', hue='Survived', palette={0: 'k', 1: 'w'})
grid = sns.FacetGrid(train_df, row='Embarked', col='Survived', size=2.2, aspect=1.6)
grid.map(sns.barplot, 'Sex', 'Fare', alpha=.5, ci=None)
grid.add_legend()


# ### Correlating categorical and numerical features 有錢無咁易死
# 
# We may also want to correlate categorical features (with non-numeric values) and numeric features. We can consider correlating Embarked (Categorical non-numeric), Sex (Categorical non-numeric), Fare (Numeric continuous), with Survived (Categorical numeric).
# 
# **Observations.**
# 
# - Higher fare paying passengers had better survival. Confirms our assumption for creating (#4) fare ranges.
# - Port of embarkation correlates with survival rates. Confirms correlating (#1) and completing (#2).
# 
# **Decisions.**
# 
# - Consider banding Fare feature.

# ## Wrangle data
# 刪除無用既特徵，會加快分析處理速度。
# 上面圖表分析發現，'Ticket' 同 'Cabin' 其實好似無咩用。所以drop 左佢地。(註: 個人認為咁樣做係要好小心，因為可以有好多數據都唔係目測得到既。 
# 
# We have collected several assumptions and decisions regarding our datasets and solution requirements. So far we did not have to change a single feature or value to arrive at these. Let us now execute our decisions and assumptions for correcting, creating, and completing goals.
# 
# ### Correcting by dropping features
# 
# This is a good starting goal to execute. By dropping features we are dealing with fewer data points. Speeds up our notebook and eases the analysis.
# 
# Based on our assumptions and decisions we want to drop the Cabin (correcting #2) and Ticket (correcting #1) features.
# 
# Note that where applicable we perform operations on both training and testing datasets together to stay consistent.

# In[17]:


print("Before", train_df.shape, test_df.shape, combine[0].shape, combine[1].shape)
train_df = train_df.drop(['Ticket', 'Cabin'], axis =1)
test_df = test_df.drop(['Ticket', 'Cabin'], axis =1)
combine = [train_df, test_df]
print("After", train_df.shape, test_df.shape, combine[0].shape, combine[1].shape)        


# In[18]:


for dataset in combine:
    dataset['Title'] = dataset.Name.str.extract(' ([A-Za-z]+)\.', expand=False)
    
pd.crosstab(train_df['Title'], train_df['Sex'])


# We can replace many titles with a more common name or classify them as `Rare`.
# 合併少數據既titles 做 `Rare`.

# In[19]:


for dataset in combine:
    dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col', 	'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')

    dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')
    
train_df[['Title', 'Survived']].groupby(['Title'], as_index=False).mean()


# We can convert the categorical titles to ordinal.
# 俾個No.list [1,2,3,4,5] 代替 [Master, Miss, Mr, Mrs, Rare]

# In[20]:


title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}
for dataset in combine:
    dataset['Title'] = dataset['Title'].map(title_mapping)
    dataset['Title'] = dataset['Title'].fillna(0)
#Title 本身唔係DataSet入面既
train_df.head()


# ## Drop走 Name 同PassengerId

# In[21]:


train_df = train_df.drop(['Name', 'PassengerId'], axis=1)
test_df = test_df.drop(['Name'], axis=1)
combine = [train_df, test_df]
train_df.shape, test_df.shape


# ### Converting a categorical feature
# 將所以名字以數值表示，例如以 1 = female ， 0 = male.
# 
# Now we can convert features which contain strings to numerical values. This is required by most model algorithms. Doing so will also help us in achieving the feature completing goal.
# 
# Let us start by converting Sex feature to a new feature called Gender where female=1 and male=0.

# In[22]:


for dataset in combine:
    dataset['Sex'] = dataset['Sex'].map( {'female': 1, 'male': 0} ).astype(int)

train_df.head()


# ### Completing a numerical continuous feature
# 開始整返的 Missing Data.有三種方法：
# 1. 均值和[標準差]之間生成隨機數
# 2. 猜測缺失值的更準確方法是使用其他相關功能。在我們的案例中，我們注意到年齡，性別和Pclass之間的相關性。
# 3. 組合方法1和2。因此，不要基於中位數猜測年齡值，而應根據Pclass和Gender組合的集合在均值和標準差之間使用隨機數。
# 4. 隨機數會有Noise加入我地既Model，次次跑都會有唔同結果，我地以家用住方法二先。
# 
# Now we should start estimating and completing features with missing or null values. We will first do this for the Age feature.
# 
# We can consider three methods to complete a numerical continuous feature.
# 
# 1. A simple way is to generate random numbers between mean and [standard deviation](https://en.wikipedia.org/wiki/Standard_deviation).
# 
# 2. More accurate way of guessing missing values is to use other correlated features. In our case we note correlation among Age, Gender, and Pclass. Guess Age values using [median](https://en.wikipedia.org/wiki/Median) values for Age across sets of Pclass and Gender feature combinations. So, median Age for Pclass=1 and Gender=0, Pclass=1 and Gender=1, and so on...
# 
# 3. Combine methods 1 and 2. So instead of guessing age values based on median, use random numbers between mean and standard deviation, based on sets of Pclass and Gender combinations.
# 
# Method 1 and 3 will introduce random noise into our models. The results from multiple executions might vary. We will prefer method 2.

# In[23]:


# grid = sns.FacetGrid(train_df, col='Pclass', hue='Gender')
# 處理緊 Age Miss 左 data 既問題 
# check check 相關性
grid = sns.FacetGrid(train_df, row='Pclass', col='Sex', size=2.2, aspect=1.6)
grid.map(plt.hist, 'Age', alpha=.5, bins=20)
grid.add_legend()


# In[24]:


# 整個 matrix 先
guess_ages = np.zeros((2,3))
guess_ages


# In[25]:


for dataset in combine:
    for i in range(0, 2):
        for j in range(0, 3):
            guess_df = dataset[(dataset['Sex'] == i) &                                   (dataset['Pclass'] == j+1)]['Age'].dropna()

            # age_mean = guess_df.mean()
            # age_std = guess_df.std()
            # age_guess = rnd.uniform(age_mean - age_std, age_mean + age_std)

            age_guess = guess_df.median()

            # Convert random age float to nearest .5 age
            guess_ages[i,j] = int( age_guess/0.5 + 0.5 ) * 0.5
            
    for i in range(0, 2):
        for j in range(0, 3):
            dataset.loc[ (dataset.Age.isnull()) & (dataset.Sex == i) & (dataset.Pclass == j+1),                    'Age'] = guess_ages[i,j]

    dataset['Age'] = dataset['Age'].astype(int)

train_df.head()


# In[26]:


train_df.info()
# Missing Age 已經補返哂


# ## Let us create Age bands and determine correlations with Survived.
# ## 將年齡分開幾份。

# In[27]:


train_df['AgeBand'] = pd.cut(train_df['Age'], 5)
train_df[['AgeBand', 'Survived']].groupby(['AgeBand'], as_index=False).mean().sort_values(by='AgeBand', ascending=True)


# In[28]:


for dataset in combine:    
    dataset.loc[ dataset['Age'] <= 16, 'Age'] = 0
    dataset.loc[(dataset['Age'] > 16) & (dataset['Age'] <= 32), 'Age'] = 1
    dataset.loc[(dataset['Age'] > 32) & (dataset['Age'] <= 48), 'Age'] = 2
    dataset.loc[(dataset['Age'] > 48) & (dataset['Age'] <= 64), 'Age'] = 3
    dataset.loc[ dataset['Age'] > 64, 'Age']
train_df.head()


# ## We can now remove the AgeBand feature.
# ## 可以刪除左AgeBand 佢

# In[29]:


train_df = train_df.drop(['AgeBand'], axis=1)
combine = [train_df, test_df]
train_df.head()


# In[30]:


train_df.head(500)


# ### Create new feature combining existing features
# 
# We can create a new feature for FamilySize which combines Parch and SibSp. This will enable us to drop Parch and SibSp from our datasets.
# 
# 合併 Parch 同 SibSp 點解？我估係因為Parch 同SibSp 相關性好高。

# In[31]:


for dataset in combine:
    dataset['FamilySize'] = dataset['SibSp'] + dataset['Parch'] + 1
    #點解+1? 個1係你自己
train_df[['FamilySize', 'Survived']].groupby(['FamilySize'], as_index=False).mean().sort_values(by='Survived', ascending=False)


# In[32]:


for dataset in combine:
    dataset['IsAlone'] = 0
    dataset.loc[dataset['FamilySize'] == 1, 'IsAlone'] = 1

train_df[['IsAlone', 'Survived']].groupby(['IsAlone'], as_index=False).mean()
#將 Family 簡化到去 Alone 同 not Alone


# Let us drop Parch, SibSp, and FamilySize features in favor of IsAlone.
# 
# Drop 哂d 舊既特徵啦~~

# In[33]:


train_df = train_df.drop(['Parch', 'SibSp', 'FamilySize'], axis=1)
test_df = test_df.drop(['Parch', 'SibSp', 'FamilySize'], axis=1)
combine = [train_df, test_df]

train_df.head()


# In[34]:


#We can also create an artificial feature combining Pclass and Age.
for dataset in combine:
    dataset['Age*Class'] = dataset.Age * dataset.Pclass

train_df.loc[:, ['Age*Class', 'Age', 'Pclass']].head(10)


# In[35]:


train_df.head()


# ### Completing a categorical feature
# 解決Embarked 特徵缺少既問題，就咁將缺少Embarked 既 Data 填最多人既港口個個
# 
# Embarked feature takes S, Q, C values based on port of embarkation. Our training dataset has two missing values. We simply fill these with the most common occurance.

# In[36]:


#邊個港口最多
freq_port = train_df.Embarked.dropna().mode()[0]
freq_port


# In[37]:


for dataset in combine:
    dataset['Embarked'] = dataset['Embarked'].fillna(freq_port)
    
train_df[['Embarked', 'Survived']].groupby(['Embarked'], as_index=False).mean().sort_values(by='Survived', ascending=False)


# In[38]:


#變做數字
for dataset in combine:
    dataset['Embarked'] = dataset['Embarked'].map( {'S': 0, 'C': 1, 'Q': 2} ).astype(int)

train_df.head()


# ### Quick completing and converting a numeric feature
# 四捨五入票價，輕鬆
# 
# We can now complete the Fare feature for single missing value in test dataset using mode to get the value that occurs most frequently for this feature. We do this in a single line of code.
# 
# Note that we are not creating an intermediate new feature or doing any further analysis for correlation to guess missing feature as we are replacing only a single value. The completion goal achieves desired requirement for model algorithm to operate on non-null values.
# 
# We may also want round off the fare to two decimals as it represents currency.

# In[39]:


test_df['Fare'].fillna(test_df['Fare'].dropna().median(), inplace=True)
test_df.head()


# In[40]:


train_df['FareBand'] = pd.qcut(train_df['Fare'], 4)
train_df[['FareBand', 'Survived']].groupby(['FareBand'], as_index=False).mean().sort_values(by='FareBand', ascending=True)


# In[41]:


# 邊票價做 4組票價
for dataset in combine:
    dataset.loc[ dataset['Fare'] <= 7.91, 'Fare'] = 0
    dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
    dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare']   = 2
    dataset.loc[ dataset['Fare'] > 31, 'Fare'] = 3
    dataset['Fare'] = dataset['Fare'].astype(int)

train_df = train_df.drop(['FareBand'], axis=1)
combine = [train_df, test_df]
    
train_df.head(10)


# In[42]:


test_df.head(10)


# ## 終於做完特徵分析!!!!!
# ## 進入Model

# ## Model, predict and solve
# 
# Now we are ready to train a model and predict the required solution. There are 60+ predictive modelling algorithms to choose from. We must understand the type of problem and solution requirement to narrow down to a select few models which we can evaluate. Our problem is a classification and regression problem. We want to identify relationship between output (Survived or not) with other variables or features (Gender, Age, Port...). We are also perfoming a category of machine learning which is called supervised learning as we are training our model with a given dataset. With these two criteria - Supervised Learning plus Classification and Regression, we can narrow down our choice of models to a few. These include:
# 
# - Logistic Regression
# - KNN or k-Nearest Neighbors
# - Support Vector Machines
# - Naive Bayes classifier
# - Decision Tree
# - Random Forrest
# - Perceptron
# - Artificial neural network
# - RVM or Relevance Vector Machine

# In[43]:


X_train = train_df.drop("Survived", axis=1)
Y_train = train_df["Survived"]
X_test  = test_df.drop("PassengerId", axis=1).copy()
X_train.shape, Y_train.shape, X_test.shape


# In[44]:


# Logistic Regression
#Note the confidence score generated by the model based on our training dataset.
logreg = LogisticRegression()
logreg.fit(X_train, Y_train)
Y_pred = logreg.predict(X_test)
acc_log = round(logreg.score(X_train, Y_train) * 100, 2)
acc_log


# In[45]:


coeff_df = pd.DataFrame(train_df.columns.delete(0))
coeff_df.columns = ['Feature']
coeff_df["Correlation"] = pd.Series(logreg.coef_[0])

coeff_df.sort_values(by='Correlation', ascending=False)


# We can use Logistic Regression to validate our assumptions and decisions for feature creating and completing goals. This can be done by calculating the coefficient of the features in the decision function.
# 
# Positive coefficients increase the log-odds of the response (and thus increase the probability), and negative coefficients decrease the log-odds of the response (and thus decrease the probability).
# 
# - Sex is highest positivie coefficient, implying as the Sex value increases (male: 0 to female: 1), the probability of Survived=1 increases the most.
# - Inversely as Pclass increases, probability of Survived=1 decreases the most.
# - This way Age*Class is a good artificial feature to model as it has second highest negative correlation with Survived.
# - So is Title as second highest positive correlation.

# In[46]:


# Support Vector Machines

svc = SVC()
svc.fit(X_train, Y_train)
Y_pred = svc.predict(X_test)
acc_svc = round(svc.score(X_train, Y_train) * 100, 2)
acc_svc


# In[47]:


knn = KNeighborsClassifier(n_neighbors = 3)
knn.fit(X_train, Y_train)
Y_pred = knn.predict(X_test)
acc_knn = round(knn.score(X_train, Y_train) * 100, 2)
acc_knn


# In[56]:


# Gaussian Naive Bayes

gaussian = GaussianNB()
gaussian.fit(X_train, Y_train)
Y_pred = gaussian.predict(X_test)
acc_gaussian = round(gaussian.score(X_train, Y_train) * 100, 2)
acc_gaussian


# In[49]:


# Perceptron

perceptron = Perceptron()
perceptron.fit(X_train, Y_train)
Y_pred = perceptron.predict(X_test)
acc_perceptron = round(perceptron.score(X_train, Y_train) * 100, 2)
acc_perceptron


# In[50]:


# Linear SVC

linear_svc = LinearSVC()
linear_svc.fit(X_train, Y_train)
Y_pred = linear_svc.predict(X_test)
acc_linear_svc = round(linear_svc.score(X_train, Y_train) * 100, 2)
acc_linear_svc


# In[51]:


# Stochastic Gradient Descent

sgd = SGDClassifier()
sgd.fit(X_train, Y_train)
Y_pred = sgd.predict(X_test)
acc_sgd = round(sgd.score(X_train, Y_train) * 100, 2)
acc_sgd


# In[58]:


# Decision Tree

decision_tree = DecisionTreeClassifier()
decision_tree.fit(X_train, Y_train)
Y_pred = decision_tree.predict(X_test)
acc_decision_tree = round(decision_tree.score(X_train, Y_train) * 100, 2)
acc_decision_tree


# In[53]:


# Random Forest

random_forest = RandomForestClassifier(n_estimators=100)
random_forest.fit(X_train, Y_train)
Y_pred = random_forest.predict(X_test)
random_forest.score(X_train, Y_train)
acc_random_forest = round(random_forest.score(X_train, Y_train) * 100, 2)
acc_random_forest


# In[54]:


models = pd.DataFrame({
    'Model': ['Support Vector Machines', 'KNN', 'Logistic Regression', 
              'Random Forest', 'Naive Bayes', 'Perceptron', 
              'Stochastic Gradient Decent', 'Linear SVC', 
              'Decision Tree'],
    'Score': [acc_svc, acc_knn, acc_log, 
              acc_random_forest, acc_gaussian, acc_perceptron, 
              acc_sgd, acc_linear_svc, acc_decision_tree]})
models.sort_values(by='Score', ascending=False)


# In[60]:


submission = pd.DataFrame({
        "PassengerId": test_df["PassengerId"],
        "Survived": Y_pred
    })
submission.to_csv('submission.csv', index=False)
print('OK la~')


# In[ ]:





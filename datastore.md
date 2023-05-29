# user info
- email
- childrenObject (embedded object)
	- uuid (key)
		- childName
		- yearOfBirth
		- photoUrl
		- createdAt
- createdAt

# user learning
- email
- childId (uuid)
- completedLessonsObject (object)
	- lessonId (key)
		- count
- tagScoring (object)
	- `<nama_tag>: {skor: ...}`
- weeklyLearningIndex (object)
	- integer: 
	- lastUpdatedDate

# lesson
- lessonId
- lessonType
- lessonLevel (int)
	- diskusi:
		- jika ada update level apakah perlu ganti langsung questionList atau buat baru item lesson
- questionIdList (list of object)
	- questionId

# question
- questionId
- questionType
- questionDetails (object)
	- question
	- answer
- tag

# report (on-demand, ngga disimpen di db)
- email
- childId
- lessonsThatNeedHelp (list)
	- tag
- weeklyLearningActivity (nested)
	- Senin: true
	- Selasa: true
	- ...

# API
- buat nerima data learning (android push setiap abis lesson selesai)
	- lessonId
	- questions
		- ...
- buat API buat android nge-get data soal
	- format mirip sama kayak yang ada di clickup kurikulum

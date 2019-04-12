# Record it

## 角色与权限

### 权限

|    操作    |        权限名称        |      说明      |
| :--------: | :--------------------: | :------------: |
|    评分    |         RECORD         |   对报告评分   |
|  上传附件  |         UPLOAD         |    上传附件    |
|  用户管理  |     MODERATOR_USER     |  管理用户权限  |
|  课程管理  |    MODERATOR_COURSE    |  管理课程权限  |
|  课程管理  |    MODERATOR_REPORT    |  管理报告权限  |
|  课程管理  | MODERATOR_RECORD_TABLE | 管理记录表权限 |
|  日志管理  |     MODERATOR_LOG      |   日志管理等   |
| 管理员权限 |       ADMINISTER       |    最高权限    |

### 角色

| 中文名称 |   英文名称    |                                                  拥有权限                                                   |                            说明                            |
| :------: | :-----------: | :---------------------------------------------------------------------------------------------------------: | :--------------------------------------------------------: |
|   访客   |     Guest     |                                               仅可以浏览页面                                                |                         未登入用户                         |
|   学生   |    Student    |                                               RECORD, UPLOAD                                                |                  注册后用户获得的默认角色                  |
|   教师   |    Teacher    |              RECORD, UPLOAD, MODERATOR_COURSE, MODERATOR_REPORT, MODERATOR_RECORD_TABLE               | 除了普通用户的权限外，还可以管理所开设的课程，报告和记录表 |
|  管理员  | Administrator | RECORD, UPLOAD, MODERATOR_COURSE, MODERATOR_REPORT, MODERATOR_RECORD_TABLE, MODERATOR_LOG, ADMINISTER |                  拥有所有权限的网站管理员                  |

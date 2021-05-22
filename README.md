# Sable

**Sable is a testing tool for SQL**, which is committed to providing a simple and user-friendly solution for testing SQL queries.

By design, the user would specify his/her test cases in an easy-to-read YAML file, and `sable` will run those test cases and generate a report.

For example, given a test file under the demo folder named test_find_email.yaml, the user should be able to use `sable demo/test_find_email.yaml` to run tests and get results printed in the console.

*Please note that the sable project is still in the planning stage and interfaces may be changed in the future.*

# Test Case Defination

## Test Suite

Each YAML document will be considered as a test suite. It should be an associative array that contains at least `version`, `suite`, `cases` as keys.

- The value in `version` is referring to the version of test define schema.
- The value in `suite` is the name of this test suite.
- The value in `cases` should be a list of test cases.

## Test Case

The test case is also been defined in an associative array. It is mandatory to include `uid`, `sql` and `exp`, and other keys are optional: `msg`, `var`, `env`.

### uid

Unique Identifier (uid) is the key that will show in the final result and it helps the user quickly find the test case definition in files.

### msg

Message (msg) will show to the user when the test cases if failed.

### sql

SQL query or SQL query template which will be executed for testing.

It is a good practice to split the code and the tests. So, sable allows users to define SQL query in a separate file and use `!file` followed by file path to identify the file.

For example, given a SQL stored in find_email.sql under the same folder demo with the test definition YAML, the test case can be written as:

```yaml
sql: !file find_email.sql
```

### var

If using a template in SQL, this is the place to set the actual value.

For example:

Given a SQL query template:

```sql
SELECT ${x} + ${y}
```

When specifying `var` as the following:

```yaml
var:
  x: 1
  y: 2
```

The SQL be executed will become:

```sql
SELECT 1 + 2
```

### env

The pre-defined environment before executing SQL query. It should be a list of associative arrays. Each member in the list represents a table, which should contain a DDL in `metadata` and tabulation-like data in `records`.

To give tabulation-like data in YAML, users can use `!fwf` and `!csv`.

For example:

```yaml
records: !fwf |
  user_id   first_name  last_name
  1         Jack        Ma
  2         Tony        Ma
  3         Robin       Li
```

```yaml
records: !csv |
  user_id,email
  1,jack_ma@alibaba.com
  2,tony_ma@qq.com
  6,robin_li@baidu.com
```

### exp

Expected result (exp) defines `where` to inspect and what `records` should the program expected to see.

For example:

```yaml
where: result set
records: !fwf |
  mail
  jack_ma@alibaba.com
  tony_ma@qq.com
```

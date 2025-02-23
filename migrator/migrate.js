const sqlite3 = require("sqlite3").verbose();
const { Client } = require("pg");

const SQLITE_PATH = process.argv[2];
const PG_URL = process.argv[3];

async function migrate() {
  const sqliteDb = new sqlite3.Database(SQLITE_PATH);

  const pgClient = new Client(PG_URL);
  await pgClient.connect();

  try {
    const tables = await new Promise((resolve, reject) => {
      sqliteDb.all(
        "SELECT name FROM sqlite_master WHERE type='table'",
        (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        },
      );
    });

    for (const table of tables) {
      const tableName = table.name;

      const safeTableName = getSafeIdentifier(tableName);
      console.log(`table: ${tableName} -> ${safeTableName}`);

      if (tableName === "migratehistory" || tableName === "alembic_version") {
        console.log("  - skipping: migration table");
        continue;
      }

      // Check if table exists first
      const tableExists = await pgClient.query(
        `SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_name = $1
        )`,
        [safeTableName],
      );

      if (tableExists.rows[0].exists) {
        const result = await pgClient.query(
          `SELECT COUNT(*) FROM ${safeTableName}`,
        );
        const rowCount = parseInt(result.rows[0].count, 10);

        if (rowCount > 0) {
          console.log(`  - skipping table: has ${rowCount} existing rows`);
          continue;
        }
      }

      console.log("  - migrating");

      const pgSchema = await pgClient.query(
        `SELECT column_name, data_type
         FROM information_schema.columns
         WHERE table_name = $1`,
        [tableName],
      );

      const pgColumnTypes = {};
      pgSchema.rows.forEach((col) => {
        pgColumnTypes[col.column_name] = col.data_type;
      });

      printPgColumnTypes(pgColumnTypes);

      const sqliteSchema = await new Promise((resolve, reject) => {
        sqliteDb.all(`PRAGMA table_info(${safeTableName})`, (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      const columns = sqliteSchema
        .map(
          (col) => `${getSafeIdentifier(col.name)} ${sqliteToPgType(col.type)}`,
        )
        .join(", ");

      await pgClient.query(
        `CREATE TABLE IF NOT EXISTS ${safeTableName} (${columns})`,
      );

      const rows = await new Promise((resolve, reject) => {
        sqliteDb.all(`SELECT * FROM ${safeTableName}`, (err, rows) => {
          if (err) reject(err);
          else resolve(rows);
        });
      });

      for (const row of rows) {
        const columns = Object.keys(row).map(getSafeIdentifier).join(", ");

        const values = Object.entries(row)
          .map(([key, value]) => {
            const columnType = pgColumnTypes[key];

            if (columnType === "boolean") {
              return value === 1 ? "true" : "false";
            }

            if (value === null) return "NULL";

            if (typeof value === "string") {
              return `'${value.replaceAll("'", "''")}'`;
            } else {
              return value;
            }
          })
          .join(", ");

        await pgClient.query(
          `INSERT INTO ${safeTableName} (${columns}) VALUES (${values})`,
        );
      }

      console.log(`Migrated ${rows.length} rows from ${tableName}`);
    }

    console.log("Migration completed successfully!");
  } catch (error) {
    console.error("Error during migration:", error);
  } finally {
    sqliteDb.close();
    await pgClient.end();
  }
}

function printPgColumnTypes(columns) {
  console.log("  - columns (POSTGRES)");
  Object.keys(columns).map((name) => {
    console.log(`    ${name}: ${columns[name]}`);
  });
}

function sqliteToPgType(sqliteType) {
  switch (sqliteType.toUpperCase()) {
    case "INTEGER":
      return "INTEGER";
    case "REAL":
      return "DOUBLE PRECISION";
    case "TEXT":
      return "TEXT";
    case "BLOB":
      return "BYTEA";
    default:
      return "TEXT";
  }
}

function getSafeIdentifier(identifier) {
  const reservedKeywords = [
    "user",
    "group",
    "order",
    "table",
    "select",
    "where",
    "from",
    "index",
    "constraint",
  ];
  return reservedKeywords.includes(identifier.toLowerCase())
    ? `"${identifier}"`
    : identifier;
}

migrate();

<?php
// Boots Eloquent (illuminate/database, installed in .cache/eloquent) against the course database,
// so Laravel snippets on the slides run for real. TUT_ENGINE / TUT_DB / TUT_MODELS come from kit.py.
require __DIR__ . '/eloquent/vendor/autoload.php';

use Illuminate\Database\Capsule\Manager as Capsule;
use Illuminate\Events\Dispatcher;
use Illuminate\Container\Container;

$capsule = new Capsule;
$engine = getenv('TUT_ENGINE') ?: 'mysql';
$capsule->addConnection($engine === 'pgsql'
    ? ['driver' => 'pgsql', 'host' => getenv('PGHOST') ?: '127.0.0.1', 'port' => getenv('PGPORT') ?: 5432,
       'database' => getenv('TUT_DB'), 'username' => getenv('PGUSER') ?: get_current_user(), 'password' => '']
    : ['driver' => 'mysql', 'host' => '127.0.0.1', 'database' => getenv('TUT_DB'), 'username' => 'root',
       'password' => '', 'charset' => 'utf8mb4', 'collation' => 'utf8mb4_0900_ai_ci']);
$capsule->setEventDispatcher(new Dispatcher(new Container));
$capsule->setAsGlobal();
$capsule->bootEloquent();
class_alias(Capsule::class, 'DB');

/** Run $fn and print every SQL query it sent (bindings filled in), like Debugbar/Telescope. */
function queries(callable $fn): mixed
{
    DB::connection()->flushQueryLog();
    DB::connection()->enableQueryLog();
    $result = $fn();
    $log = DB::connection()->getQueryLog();
    DB::connection()->disableQueryLog();
    foreach ($log as $i => $q) {
        $sql = $q['query'];
        foreach ($q['bindings'] as $b) {
            $v = is_int($b) || is_float($b) ? $b : "'" . $b . "'";
            $sql = preg_replace('/\?/', (string) $v, $sql, 1);
        }
        echo '[' . ($i + 1) . '] ' . $sql . "\n";
    }
    echo '→ মোট query: ' . count($log) . "\n";
    return $result;
}

if ($models = getenv('TUT_MODELS')) {
    require $models;
}

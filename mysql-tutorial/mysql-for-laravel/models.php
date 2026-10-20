<?php
// Eloquent models for the 'Rahim Mobile' schema (../shop_schema.py). Loaded before every Laravel snippet.

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Branch extends Model
{
    public $timestamps = false;
    public function sales() { return $this->hasMany(Sale::class); }
    public function employees() { return $this->hasMany(Employee::class); }
}

class Customer extends Model
{
    public $timestamps = false;
    protected $fillable = ['name', 'phone', 'district'];
    public function sales() { return $this->hasMany(Sale::class); }
}

class Category extends Model
{
    public $timestamps = false;
    public function products() { return $this->hasMany(Product::class); }
}

class Product extends Model
{
    public $timestamps = false;
    protected $fillable = ['category_id', 'name', 'brand', 'cost', 'price', 'stock'];
    public function category() { return $this->belongsTo(Category::class); }
    public function saleItems() { return $this->hasMany(SaleItem::class); }
}

class Employee extends Model
{
    public $timestamps = false;
    public function branch() { return $this->belongsTo(Branch::class); }
    public function sales() { return $this->hasMany(Sale::class); }
}

class Sale extends Model
{
    public $timestamps = false;
    public function customer() { return $this->belongsTo(Customer::class); }
    public function branch() { return $this->belongsTo(Branch::class); }
    public function employee() { return $this->belongsTo(Employee::class); }
    public function items() { return $this->hasMany(SaleItem::class); }
}

class SaleItem extends Model
{
    public $timestamps = false;
    public function sale() { return $this->belongsTo(Sale::class); }
    public function product() { return $this->belongsTo(Product::class); }
}

class Expense extends Model
{
    use SoftDeletes;
    protected $fillable = ['title', 'amount'];
}

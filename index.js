const express = require('express');
const { Sequelize, DataTypes } = require('sequelize');
const bodyParser = require('body-parser');
const moment = require('moment');

// Initialize Express app
const app = express();
app.set('view engine', 'ejs');
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Initialize SQLite database
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: './catering.db'
});

// Models

// 1. Cost Categories model
const CostCategory = sequelize.define('CostCategory', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  }
});

// 2. Nomenclature model
const Nomenclature = sequelize.define('Nomenclature', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  costCategoryId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: CostCategory,
      key: 'id'
    }
  }
});

// 3. Supplier model
const Supplier = sequelize.define('Supplier', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  costCategoryId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: CostCategory,
      key: 'id'
    }
  }
});

// 4. Price model
const Price = sequelize.define('Price', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  supplierId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Supplier,
      key: 'id'
    }
  },
  nomenclatureId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Nomenclature,
      key: 'id'
    }
  },
  price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  date: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  }
});

// 5. Event model
const Event = sequelize.define('Event', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  name: {
    type: DataTypes.STRING,
    allowNull: false
  },
  date: {
    type: DataTypes.DATEONLY,
    allowNull: false
  },
  startTime: {
    type: DataTypes.TIME,
    allowNull: false
  },
  expectedGuests: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  budget: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  description: {
    type: DataTypes.TEXT
  }
});

// 6. Order model
const Order = sequelize.define('Order', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  eventId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Event,
      key: 'id'
    }
  },
  orderDate: {
    type: DataTypes.DATE,
    defaultValue: DataTypes.NOW
  },
  orderNumber: {
    type: DataTypes.STRING,
    allowNull: false
  }
});

// 7. Order Item model (for the tabular part of orders)
const OrderItem = sequelize.define('OrderItem', {
  id: {
    type: DataTypes.INTEGER,
    primaryKey: true,
    autoIncrement: true
  },
  orderId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Order,
      key: 'id'
    }
  },
  nomenclatureId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Nomenclature,
      key: 'id'
    }
  },
  quantity: {
    type: DataTypes.INTEGER,
    allowNull: false
  },
  price: {
    type: DataTypes.DECIMAL(10, 2),
    allowNull: false
  },
  supplierId: {
    type: DataTypes.INTEGER,
    allowNull: false,
    references: {
      model: Supplier,
      key: 'id'
    }
  }
});

// Define associations
CostCategory.hasMany(Nomenclature, { foreignKey: 'costCategoryId' });
Nomenclature.belongsTo(CostCategory, { foreignKey: 'costCategoryId' });

CostCategory.hasMany(Supplier, { foreignKey: 'costCategoryId' });
Supplier.belongsTo(CostCategory, { foreignKey: 'costCategoryId' });

Supplier.hasMany(Price, { foreignKey: 'supplierId' });
Nomenclature.hasMany(Price, { foreignKey: 'nomenclatureId' });
Price.belongsTo(Supplier);
Price.belongsTo(Nomenclature);

Event.hasMany(Order, { foreignKey: 'eventId' });
Order.belongsTo(Event);

Order.hasMany(OrderItem, { foreignKey: 'orderId' });
OrderItem.belongsTo(Order);

Nomenclature.hasMany(OrderItem, { foreignKey: 'nomenclatureId' });
OrderItem.belongsTo(Nomenclature);

Supplier.hasMany(OrderItem, { foreignKey: 'supplierId' });
OrderItem.belongsTo(Supplier);

// Routes

// Home page
app.get('/', async (req, res) => {
  res.render('index');
});

// Cost Categories routes
app.get('/categories', async (req, res) => {
  const categories = await CostCategory.findAll();
  res.render('categories/index', { categories });
});

app.get('/categories/new', (req, res) => {
  res.render('categories/new');
});

app.post('/categories', async (req, res) => {
  await CostCategory.create(req.body);
  res.redirect('/categories');
});

// Nomenclature routes
app.get('/nomenclature', async (req, res) => {
  const nomenclatures = await Nomenclature.findAll({
    include: [{ model: CostCategory }]
  });
  const categories = await CostCategory.findAll();
  res.render('nomenclature/index', { nomenclatures, categories });
});

app.get('/nomenclature/new', async (req, res) => {
  const categories = await CostCategory.findAll();
  res.render('nomenclature/new', { categories });
});

app.post('/nomenclature', async (req, res) => {
  await Nomenclature.create(req.body);
  res.redirect('/nomenclature');
});

// Suppliers routes
app.get('/suppliers', async (req, res) => {
  const suppliers = await Supplier.findAll({
    include: [{ model: CostCategory }]
  });
  const categories = await CostCategory.findAll();
  res.render('suppliers/index', { suppliers, categories });
});

app.get('/suppliers/new', async (req, res) => {
  const categories = await CostCategory.findAll();
  res.render('suppliers/new', { categories });
});

app.post('/suppliers', async (req, res) => {
  await Supplier.create(req.body);
  res.redirect('/suppliers');
});

// Prices routes
app.get('/prices', async (req, res) => {
  const prices = await Price.findAll({
    include: [
      { model: Supplier, include: [{ model: CostCategory }] },
      { model: Nomenclature, include: [{ model: CostCategory }] }
    ]
  });
  res.render('prices/index', { prices });
});

app.get('/prices/new', async (req, res) => {
  const suppliers = await Supplier.findAll({ include: [{ model: CostCategory }] });
  const nomenclatures = await Nomenclature.findAll({ include: [{ model: CostCategory }] });
  res.render('prices/new', { suppliers, nomenclatures });
});

app.post('/prices', async (req, res) => {
  req.body.date = new Date(); // Set current date
  await Price.create(req.body);
  res.redirect('/prices');
});

// Events routes
app.get('/events', async (req, res) => {
  const events = await Event.findAll();
  res.render('events/index', { events });
});

app.get('/events/new', (req, res) => {
  res.render('events/new');
});

app.post('/events', async (req, res) => {
  await Event.create(req.body);
  res.redirect('/events');
});

// Orders routes
app.get('/orders', async (req, res) => {
  const orders = await Order.findAll({
    include: [{ model: Event }]
  });
  res.render('orders/index', { orders });
});

app.get('/orders/new', async (req, res) => {
  const events = await Event.findAll();
  const nomenclatures = await Nomenclature.findAll({ include: [{ model: CostCategory }] });
  const suppliers = await Supplier.findAll({ include: [{ model: CostCategory }] });
  
  res.render('orders/new', { 
    events, 
    nomenclatures, 
    suppliers,
    orderItems: [] // Initially empty
  });
});

app.post('/orders', async (req, res) => {
  // Create the order
  const order = await Order.create({
    eventId: req.body.eventId,
    orderNumber: req.body.orderNumber,
    orderDate: new Date()
  });
  
  // Process order items
  const { nomenclatureIds, quantities, prices, supplierIds } = req.body;
  
  if (nomenclatureIds && Array.isArray(nomenclatureIds)) {
    for (let i = 0; i < nomenclatureIds.length; i++) {
      if (nomenclatureIds[i]) {
        await OrderItem.create({
          orderId: order.id,
          nomenclatureId: parseInt(nomenclatureIds[i]),
          quantity: parseInt(quantities[i]),
          price: parseFloat(prices[i]),
          supplierId: parseInt(supplierIds[i])
        });
      }
    }
  }
  
  res.redirect('/orders');
});

// Report route
app.get('/reports', async (req, res) => {
  const events = await Event.findAll();
  
  // Calculate expenses per event and category
  const reportData = [];
  
  for (const event of events) {
    const orders = await Order.findAll({
      where: { eventId: event.id },
      include: [{
        model: OrderItem,
        include: [
          { model: Nomenclature, include: [{ model: CostCategory }] },
          { model: Supplier, include: [{ model: CostCategory }] }
        ]
      }]
    });
    
    // Calculate total expenses by category
    const categoryExpenses = {};
    let totalExpense = 0;
    
    for (const order of orders) {
      for (const item of order.OrderItems) {
        const categoryName = item.Nomenclature.CostCategory.name;
        const itemTotal = item.quantity * parseFloat(item.price);
        
        if (!categoryExpenses[categoryName]) {
          categoryExpenses[categoryName] = 0;
        }
        
        categoryExpenses[categoryName] += itemTotal;
        totalExpense += itemTotal;
      }
    }
    
    reportData.push({
      event: event,
      totalBudget: parseFloat(event.budget),
      totalExpense: totalExpense,
      categoryExpenses: categoryExpenses,
      exceedsBudget: totalExpense > parseFloat(event.budget)
    });
  }
  
  res.render('reports/index', { reportData });
});

// Sync database and start server
const PORT = process.env.PORT || 3000;

// Initialize database and create test data
async function initializeDatabase() {
  try {
    await sequelize.sync({ force: true }); // This will recreate tables
    
    // Create default cost categories
    const categoriesData = [
      { name: 'Продукты/готовые блюда' },
      { name: 'Напитки' },
      { name: 'Оборудование' },
      { name: 'Персонал' },
      { name: 'Транспорт' },
      { name: 'Прочие расходы' }
    ];
    
    for (const cat of categoriesData) {
      await CostCategory.create(cat);
    }
    
    console.log('Database initialized with default categories');
  } catch (error) {
    console.error('Error initializing database:', error);
  }
}

initializeDatabase().then(() => {
  app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
  });
});

module.exports = app;
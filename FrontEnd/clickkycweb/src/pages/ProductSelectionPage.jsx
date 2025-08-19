import React, { useState, useEffect } from 'react';
import { getProductList } from '../services/kycService';
import {Truncate} from '../utils/helpers'
import '../CSS/ProductSelection.css';

const ProductSelection = ({ onNext, updateFormData, showModal, setIsLoading, updateStepStatus }) => {
    const [products, setProducts] = useState([]);
    const [selectedProduct, setSelectedProduct] = useState(null);
    const [modal, setModal] = useState({
            title: '',
            content: ''
        });
    
    if(modal.title !== '' && modal.content !== ''){
        showModal(modal.title, modal.content)
    }

    useEffect(() => {
        const fetchProducts = async () => {
        try {
            setIsLoading(true);
            const response = await getProductList('Deposit');
            if (response.Status === 'OK') {
            setProducts(response.Result);
            } else {
            setModal(modal.title = 'Error', modal.content = response.Message);
            }
        } catch (err) {
            setModal(modal.title = 'Error', modal.content = 'Failed to fetch products');
        } finally {
            setIsLoading(false);
        }
        };

        fetchProducts();
    }, [setIsLoading, modal]);

    const handleProductClick = (product) => {
        setSelectedProduct(product);
        showModal(product.product_name, product.description);
    };

    const handleConfirmSelection = () => {
        if (selectedProduct) {
        updateFormData({ product_code: selectedProduct.product_code });
        onNext();
        }
    };


    return (
        <div className="selection-container">
            <div className="selection-header">
                <h2>Select a Product</h2>
                <p>Choose the product you want to apply for</p>
            </div>
        
        <div className="product-cards-grid">
            {products.map((product) => (
            <div 
                key={product.product_code}
                className={`product-card ${selectedProduct?.product_code === product.product_code ? 'selected' : ''}`}
                onClick={() => handleProductClick(product)}
            >
                <div className="card-icon">
                <div className="product-header">
                    <span className={`product-type ${product.product_type.toLowerCase()}`}>
                    {product.product_type}
                    </span>
                </div>
                <div className="product-icon-container">
                    <img 
                        src={product.icon_url || '/assets/images/default-product-icon.png'} 
                        alt={product.name}
                        className="product-icon"
                        onError={(e) => {
                        e.target.onerror = null; 
                        e.target.src = '/default-product-icon.png'
                        }}
                    />
                    </div>
                </div>
                <div className="card-content">
                    <h3 className="product-name">{product.product_name}</h3>
                    <div className="product-highlights">
                    <div className="highlight-badge">
                        <span className="highlight-icon">★</span>
                        <span>Popular</span>
                    </div>
                    <div className="highlight-badge">
                        <span className="highlight-icon">%</span>
                        <span>2.5% APY</span>
                    </div>
                    </div>
                    <p className="product-description">{Truncate(product.description)}</p>
                    <div className="product-footer">
                    <button className="details-button">
                        View Details →
                    </button>
                    </div>
                </div>
            </div>
            ))}
        </div>

        {selectedProduct && (
            <div className="step-action-first">
                <button 
                onClick={handleConfirmSelection} 
                className="button button-primary"
                disabled={!selectedProduct}
                >
                Submit
                </button>
            </div>
        )}
        </div>
    );
};

export default ProductSelection;
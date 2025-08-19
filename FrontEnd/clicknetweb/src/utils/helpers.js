
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(amount);
};

export const formatDate = (dateString) => {
  if (!dateString) return '';
      
  const d = new Date(dateString);
  
  if (isNaN(d.getTime())) {
    console.log('Invalid date:', dateString);
    return '';
  }

  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const finaldate = `${year}-${month}-${day}`;
  console.log(finaldate);
  return finaldate;
};

export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  
  const day = String(date.getDate()).padStart(2, '0');
  const month = date.toLocaleString('default', { month: 'short' });
  const year = date.getFullYear();
  
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  
  return `${day} ${month}, ${year} ${hours}:${minutes}:${seconds}`;
}

export const handleApiResponse = (response) => {
  if (response.data.Status === 'OK') {
    return { success: true, data: response.data.Result, message: response.data.Message };
  } else if (response.data.Status === 'FAILED') {
    return { success: false, message: response.data.Message };
  } else if (response.data.Status === 'OTP') {
    return { requiresOTP: true, message: response.data.Message };
  }
  return { success: false, message: 'Unknown response from server' };
};


export const capitalizeName = (name) => {
    return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
}


export const  formatDistance = (meters) => {
  if (meters < 1000) {
    const m = Math.ceil(meters);
    return `${m} meter${m > 1 ? "s" : ""}`;
  } else {
    const km = Math.ceil(meters / 1000);
    return `${km} kilometer${km > 1 ? "s" : ""}`;
  }
}

export const formatDuration = (seconds) =>  {
  const minutes = Math.ceil(seconds / 60);
  if (minutes < 60) {
    return `${minutes} minute${minutes > 1 ? "s" : ""}`;
  }

  const hours = Math.ceil(minutes / 60);
  if (hours < 24) {
    return `${hours} hour${hours > 1 ? "s" : ""}`;
  }

  const days = Math.ceil(hours / 24);
  return `${days} day${days > 1 ? "s" : ""}`;
}
